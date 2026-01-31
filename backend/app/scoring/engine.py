from __future__ import annotations
from typing import Dict,Any,Tuple,List
import os,yaml

def clamp01(x:float)->float:
    return max(0.0,min(1.0,x))

def readiness_class(hri:float)->str:
    """Classify readiness using HRI bands:
    0–40   → Not Ready
    41–69  → Conditionally Ready
    70–85  → Ready with Controls
    86–100 → Fully Ready
    """
    if hri <= 40: 
        return "Not Ready"
    if 41 <= hri <= 69:
        return "Conditionally Ready"
    if 70 <= hri <= 85:
        return "Ready with Controls"
    return "Fully Ready"

def _add(score:float,drivers:List[str],amount:float,reason:str)->float:
    if amount<=0: return score
    drivers.append(f"-{amount:.2f}: {reason}")
    return score-amount

def load_cfg()->Dict[str,Any]:
    here=os.path.dirname(__file__)
    with open(os.path.join(here,"penalties.yaml"),"r",encoding="utf-8") as f:
        return yaml.safe_load(f)

CFG=load_cfg()
WEIGHTS=CFG["weights"]

def score_M(inp:Dict[str,Any])->Tuple[float,List[str]]:
    s,d=1.0,[]
    haz=inp.get("hardness_haz_hv")
    yt=inp.get("yt_ratio")
    seam=(inp.get("seam_type") or "").lower()
    if haz is not None:
        for r in CFG["M"]["hardness"]:
            if haz>=r["min"]:
                s=_add(s,d,r["pen"],f"M: {r['label']}"); break
    if yt is not None:
        for r in CFG["M"]["yt_ratio"]:
            if yt>=r["min"]:
                s=_add(s,d,r["pen"],f"M: {r['label']}"); break
    if "pre1970" in seam or "vintage" in seam:
        s=_add(s,d,CFG["M"]["seam"]["erw_pre1970"],"M: Vintage ERW / pre-1970 seam")
    elif "erw" in seam:
        s=_add(s,d,CFG["M"]["seam"]["erw"],"M: ERW seam")
    return clamp01(s),d

def score_D(inp:Dict[str,Any])->Tuple[float,List[str]]:
    s,d=1.0,[]
    stress=inp.get("stress_ratio")
    cycles=inp.get("cycles_per_day")
    rng=inp.get("cycle_range_bar")
    surges=inp.get("surge_events_per_year")
    dpdt=inp.get("dpdt_p95_bar_per_s")
    if stress is not None:
        for r in CFG["D"]["stress_ratio"]:
            if stress>=r["min"]:
                s=_add(s,d,r["pen"],f"D: {r['label']}"); break
    if cycles is not None and rng is not None:
        for r in CFG["D"]["cycling"]:
            if cycles>=r["cycles_min"] and rng>=r["range_min"]:
                s=_add(s,d,r["pen"],f"D: {r['label']}"); break
    elif rng is not None:
        for r in CFG["D"]["range_only"]:
            if rng>=r["min"]:
                s=_add(s,d,r["pen"],f"D: {r['label']}"); break
    if surges is not None:
        for r in CFG["D"]["surges"]:
            if surges>=r["min"]:
                s=_add(s,d,r["pen"],f"D: {r['label']}"); break
    if dpdt is not None:
        for r in CFG["D"]["dpdt"]:
            if dpdt>=r["min"]:
                s=_add(s,d,r["pen"],f"D: {r['label']}"); break
    return clamp01(s),d

def score_I(inp:Dict[str,Any])->Tuple[float,List[str]]:
    s,d=1.0,[]
    metal=inp.get("max_metal_loss_pct")
    crack=inp.get("crack_density_per_km")
    crack_len=inp.get("max_crack_length_mm")
    backlog=inp.get("repair_backlog_high")
    if crack is not None:
        for r in CFG["I"]["crack_density"]:
            if crack>=r["min"]:
                s=_add(s,d,r["pen"],f"I: {r['label']}"); break
    if crack_len is not None:
        for r in CFG["I"]["crack_len"]:
            if crack_len>=r["min"]:
                s=_add(s,d,r["pen"],f"I: {r['label']}"); break
    if metal is not None:
        for r in CFG["I"]["metal_loss"]:
            if metal>=r["min"]:
                s=_add(s,d,r["pen"],f"I: {r['label']}"); break
    if backlog:
        s=_add(s,d,CFG["I"]["backlog_pen"],"I: High repair backlog / overdue repairs")
    return clamp01(s),d

def score_C(inp:Dict[str,Any])->Tuple[float,List[str]]:
    s,d=1.0,[]
    ctype=(inp.get("coating_type") or "").lower()
    cage=inp.get("coating_age_years")
    dcvg=inp.get("dcvg_anomaly_pct")
    over=inp.get("cp_overprotect_pct")
    pot=inp.get("cp_potential_avg_v")
    for k,pen in CFG["C"]["coating_type"].items():
        if k in ctype:
            s=_add(s,d,pen,f"C: {k} coating"); break
    if cage is not None:
        for r in CFG["C"]["coating_age"]:
            if cage>=r["min"]:
                s=_add(s,d,r["pen"],f"C: {r['label']}"); break
    if dcvg is not None:
        for r in CFG["C"]["dcvg"]:
            if dcvg>=r["min"]:
                s=_add(s,d,r["pen"],f"C: {r['label']}"); break
    if over is not None:
        for r in CFG["C"]["overprot"]:
            if over>=r["min"]:
                s=_add(s,d,r["pen"],f"C: {r['label']}"); break
    if pot is not None and pot<=CFG["C"]["pot_screen"]["min"]:
        s=_add(s,d,CFG["C"]["pot_screen"]["pen"],f"C: {CFG['C']['pot_screen']['label']}")
    return clamp01(s),d

def score_E(inp:Dict[str,Any])->Tuple[float,List[str]]:
    s,d=1.0,[]
    res=inp.get("soil_resistivity_ohm_cm")
    ph=inp.get("soil_ph")
    mic=(inp.get("mic_risk") or "low").lower()
    moist=inp.get("moisture_high")
    stray=(inp.get("stray_current_risk") or "low").lower()
    if res is not None:
        for r in CFG["E"]["resistivity"]:
            if res<r["max"]:
                s=_add(s,d,r["pen"],f"E: {r['label']}"); break
    if ph is not None:
        if ph<=CFG["E"]["ph"]["acid"]["max"]:
            s=_add(s,d,CFG["E"]["ph"]["acid"]["pen"],f"E: {CFG['E']['ph']['acid']['label']}")
        elif ph>=CFG["E"]["ph"]["alk"]["min"]:
            s=_add(s,d,CFG["E"]["ph"]["alk"]["pen"],f"E: {CFG['E']['ph']['alk']['label']}")
    if mic in CFG["E"]["mic"]:
        s=_add(s,d,CFG["E"]["mic"][mic],f"E: {mic.upper()} MIC risk")
    if moist:
        s=_add(s,d,CFG["E"]["moist_pen"],"E: High moisture / wet soil")
    if stray in CFG["E"]["stray"]:
        s=_add(s,d,CFG["E"]["stray"][stray],f"E: {stray.upper()} stray current risk")
    return clamp01(s),d

def score_Q(inp:Dict[str,Any])->Tuple[float,List[str]]:
    s,d=1.0,[]
    ili=inp.get("ili_coverage_pct")
    cp_age=inp.get("cp_survey_age_months")
    scada=inp.get("scada_uptime_pct")
    miss=inp.get("missing_fields_pct")
    if ili is not None:
        for r in CFG["Q"]["ili"]:
            if ili<r["max"]:
                s=_add(s,d,r["pen"],f"Q: {r['label']}"); break
    if cp_age is not None:
        for r in CFG["Q"]["cp_age"]:
            if cp_age>r["min"]:
                s=_add(s,d,r["pen"],f"Q: {r['label']}"); break
    if scada is not None:
        for r in CFG["Q"]["scada"]:
            if scada<r["max"]:
                s=_add(s,d,r["pen"],f"Q: {r['label']}"); break
    if miss is not None:
        for r in CFG["Q"]["missing"]:
            if miss>=r["min"]:
                s=_add(s,d,r["pen"],f"Q: {r['label']}"); break
    return clamp01(s),d

def score_O(inp:Dict[str,Any])->Tuple[float,List[str]]:
    s,d=1.0,[]
    plan=inp.get("has_h2_plan")
    sens=inp.get("h2_sensors")
    proc=inp.get("operating_procedure_updated")
    leak=inp.get("leak_detection_enhanced")
    train=inp.get("training_complete")
    if not plan:
        s=_add(s,d,CFG["O"]["no_plan"],"O: No hydrogen transition plan in place")
    if not sens:
        s=_add(s,d,CFG["O"]["no_sensors"],"O: No hydrogen-specific sensors/monitoring")
    if not proc:
        s=_add(s,d,CFG["O"]["no_proc"],"O: Procedures not updated for hydrogen")
    if not leak:
        s=_add(s,d,CFG["O"]["no_leak"],"O: Leak detection not enhanced for hydrogen")
    if not train:
        s=_add(s,d,CFG["O"]["no_training"],"O: Training/competency not confirmed")
    return clamp01(s),d

def compute_hri(inputs:Dict[str,Any])->Tuple[float,str,Dict[str,float],List[str]]:
    drivers:List[str]=[]
    m,dm=score_M(inputs)
    d,dd=score_D(inputs)
    i,di=score_I(inputs)
    c,dc=score_C(inputs)
    e,de=score_E(inputs)
    q,dq=score_Q(inputs)
    o,do=score_O(inputs)
    drivers+=dm+dd+di+dc+de+dq+do

    pillars={"M":m,"D":d,"I":i,"C":c,"E":e,"Q":q,"O":o}
    hri=100.0*sum(WEIGHTS[k]*pillars[k] for k in WEIGHTS)

    gating_msgs:List[str]=[]
    ki=inputs.get("ki_mpa_sqrtm")
    kth=inputs.get("kth_mpa_sqrtm")
    if ki is not None and kth is not None and ki>kth:
        old_m=pillars["M"]
        pillars["M"]=min(pillars["M"],0.30)
        if hri>40.0:
            hri=40.0
        gating_msgs.append(
            f"Gating: K_I = {ki} MPa√m exceeds K_TH = {kth} MPa√m. "
            f"Metallurgy pillar reduced from {old_m:.2f} to {pillars['M']:.2f} and HRI capped at 40."
        )
    if pillars["I"]<0.30 and hri>40.0:
        hri=40.0
        gating_msgs.append(
            f"Gating: Integrity pillar I = {pillars['I']:.2f} < 0.30. HRI limited to 40 until defects are remediated."
        )
    if pillars["Q"]<0.40 and hri>50.0:
        hri=50.0
        gating_msgs.append(
            f"Gating: Data Quality pillar Q = {pillars['Q']:.2f} < 0.40. HRI limited to 50 until data coverage improves."
        )

    drivers.extend(gating_msgs)
    hri=float(round(hri,2))
    klass=readiness_class(hri)
    return hri,klass,pillars,drivers
