import os
import requests
import pandas as pd
import streamlit as st
import altair as alt

API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")

st.set_page_config(page_title="H2Ready – Full MVP (MDCQIO)", layout="wide")
st.title("H2Ready – Full MVP (M, D, I, C, E, Q, O with K_I/K_TH Gate)")

def api_get(path, **params):
    return requests.get(f"{API_BASE}{path}", params=params, timeout=60)

def api_post(path, payload=None):
    return requests.post(f"{API_BASE}{path}", json=payload, timeout=120)

def build_narrative(pillars: dict) -> str:
    names = {
        "M": "Metallurgy (materials, HAZ hardness, seam history, K_I/K_TH)",
        "D": "Design & Operating Envelope (pressure cycles, surges, dp/dt)",
        "I": "Integrity & Defects (cracks, corrosion, repairs backlog)",
        "C": "Coatings & CP (coating type, age, anomalies, overprotection)",
        "E": "Environment (soil, MIC, moisture, stray currents)",
        "Q": "Data Quality (coverage, recency, missing fields)",
        "O": "Operational Controls (procedures, sensing, training)",
    }
    if not pillars:
        return "No pillar scores available yet."

    items = sorted(pillars.items(), key=lambda x: x[1])
    focus = [p for p, v in items if v < 0.85][:3]
    if not focus:
        return (
            "All pillars are relatively strong. Focus on continuous improvement in monitoring, early-warning analytics, "
            "and hydrogen governance to incrementally raise the HRI."
        )

    lines = ["To raise the Hydrogen Readiness Index (HRI), focus on strengthening the following low pillars:"]
    for code in focus:
        lines.append(f"- **{code}** – {names.get(code, code)}")
    lines.append(
        "Typical interventions include fracture mechanics verification & material testing (M), "
        "optimising operating envelopes and surge control (D), defect remediation and targeted inspection (I), "
        "recoating and CP tuning (C), detailed environmental characterisation (E), governance of data pipelines (Q), "
        "and enhanced procedures, sensing, and training (O)."
    )
    return "\n".join(lines)

tabs = st.tabs(["Setup", "Inputs (M, D, I, C, E, Q, O)", "Score & Dashboard"])

# SETUP TAB
with tabs[0]:
    st.subheader("Pipelines")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        pid = st.text_input("Pipeline ID", value="pipe_001")
    with col2:
        pname = st.text_input("Pipeline Name", value="Example Transmission Line")
    with col3:
        operator = st.text_input("Operator", value="")
    with col4:
        region = st.text_input("Region", value="UK")
    if st.button("Create Pipeline"):
        r = api_post("/pipelines", {"id": pid, "name": pname, "operator": operator or None, "region": region or None})
        if r.ok:
            st.success("Pipeline created")
        else:
            st.error(r.text)

    pipes = api_get("/pipelines")
    if pipes.ok and pipes.json():
        st.write("Existing pipelines:")
        st.table(pipes.json())
    else:
        st.info("No pipelines yet. Create one above.")

    st.markdown("---")
    st.subheader("Segments")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        seg_id = st.text_input("Segment ID", value="seg_001")
    with col2:
        seg_pipe = st.text_input("Pipeline for Segment", value="pipe_001")
    with col3:
        start_km = st.number_input("Start km", value=0.0)
    with col4:
        end_km = st.number_input("End km", value=5.0)
    if st.button("Create Segment"):
        r = api_post("/segments", {"id": seg_id, "pipeline_id": seg_pipe, "start_km": start_km, "end_km": end_km})
        if r.ok:
            st.success("Segment created")
        else:
            st.error(r.text)

    segs = api_get("/segments")
    if segs.ok and segs.json():
        st.write("Existing segments:")
        st.table(segs.json())
    else:
        st.info("No segments yet. Create at least one above.")

# INPUTS TAB
with tabs[1]:
    st.subheader("Segment Inputs for All 7 Pillars")
    segs = api_get("/segments")
    seg_list = [s["id"] for s in (segs.json() if segs.ok else [])]
    if not seg_list:
        st.info("Create a segment first in the Setup tab.")
    else:
        sel = st.selectbox("Select Segment", seg_list)
        cur = api_get(f"/segments/{sel}/inputs")
        inputs = cur.json().get("inputs", {}) if cur.ok else {}

        tM, tD, tI, tC, tE, tQ, tO = st.tabs(
            ["M – Metallurgy", "D – Design & Ops", "I – Integrity", "C – Coating & CP",
             "E – Environment", "Q – Data Quality", "O – Operational Controls"]
        )
        payload: dict = {}

        def num(label, key, default=0.0, **kwargs):
            payload[key] = st.number_input(label, value=float(inputs.get(key) or default), **kwargs)

        def txt(label, key):
            v = st.text_input(label, value=str(inputs.get(key) or ""))
            payload[key] = v.strip() or None

        def chk(label, key):
            payload[key] = st.checkbox(label, value=bool(inputs.get(key) or False))

        with tM:
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                txt("API Grade", "api_grade")
            with c2:
                num("SMYS (MPa)", "smys_mpa", min_value=0.0)
            with c3:
                num("Y/T Ratio", "yt_ratio", min_value=0.0, max_value=2.0)
            with c4:
                num("HAZ Hardness (HV)", "hardness_haz_hv", min_value=0.0)

            c5, c6, c7 = st.columns(3)
            with c5:
                seam = st.selectbox(
                    "Seam Type",
                    ["", "Seamless", "ERW", "Vintage ERW (pre-1970)", "SAW"],
                    index=0,
                )
                payload["seam_type"] = seam or None
            with c6:
                num("K_I (MPa√m)", "ki_mpa_sqrtm", min_value=0.0)
            with c7:
                num("K_TH (MPa√m)", "kth_mpa_sqrtm", min_value=0.0)
            st.caption(
                "If K_I exceeds K_TH, the Metallurgy pillar is capped and the overall HRI cannot exceed 40 "
                "(fracture mechanics safety gate)."
            )

        with tD:
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                num("Hoop Stress Ratio (σh/SMYS)", "stress_ratio", min_value=0.0, max_value=2.0)
            with c2:
                num("Cycles per Day", "cycles_per_day", min_value=0.0)
            with c3:
                num("Typical Cycle Range (bar)", "cycle_range_bar", min_value=0.0)
            with c4:
                num("Surge Events per Year", "surge_events_per_year", min_value=0.0)
            c5, c6 = st.columns(2)
            with c5:
                num("dp/dt P95 (bar/s)", "dpdt_p95_bar_per_s", min_value=0.0)
            with c6:
                num("Temp Min (°C)", "temp_min_c")
            num("Temp Max (°C)", "temp_max_c")

        with tI:
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                num("Max Metal Loss (% WT)", "max_metal_loss_pct", min_value=0.0, max_value=100.0)
            with c2:
                num("Crack Density (/km)", "crack_density_per_km", min_value=0.0)
            with c3:
                num("Max Crack Length (mm)", "max_crack_length_mm", min_value=0.0)
            with c4:
                chk("High Repair Backlog / Overdue Repairs", "repair_backlog_high")

        with tC:
            c1, c2, c3, c4, c5 = st.columns(5)
            with c1:
                ctype = st.selectbox(
                    "Coating Type",
                    ["", "FBE", "3LPE", "Tape", "Coal_tar"],
                    index=0,
                )
                payload["coating_type"] = ctype or None
            with c2:
                num("Coating Age (years)", "coating_age_years", min_value=0.0)
            with c3:
                num("DCVG Anomaly Area (%)", "dcvg_anomaly_pct", min_value=0.0, max_value=100.0)
            with c4:
                num("Average CP Potential (V CSE)", "cp_potential_avg_v")
            with c5:
                num("CP Overprotection (% time)", "cp_overprotect_pct", min_value=0.0, max_value=100.0)

        with tE:
            c1, c2, c3, c4, c5 = st.columns(5)
            with c1:
                num("Soil Resistivity (Ω·cm)", "soil_resistivity_ohm_cm", min_value=0.0)
            with c2:
                num("Soil pH", "soil_ph", min_value=0.0, max_value=14.0)
            with c3:
                mic = st.selectbox("MIC Risk", ["low", "medium", "high"], index=0)
                payload["mic_risk"] = mic
            with c4:
                chk("High Moisture / Wet Soil", "moisture_high")
            with c5:
                stray = st.selectbox("Stray Current Risk", ["low", "medium", "high"], index=0)
                payload["stray_current_risk"] = stray

        with tQ:
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                num("ILI Coverage (%)", "ili_coverage_pct", min_value=0.0, max_value=100.0)
            with c2:
                num("CP Survey Age (months)", "cp_survey_age_months", min_value=0.0)
            with c3:
                num("SCADA Uptime (%)", "scada_uptime_pct", min_value=0.0, max_value=100.0)
            with c4:
                num("Missing Key Fields (%)", "missing_fields_pct", min_value=0.0, max_value=100.0)

        with tO:
            c1, c2, c3, c4, c5 = st.columns(5)
            with c1:
                chk("Hydrogen Transition Plan in Place", "has_h2_plan")
            with c2:
                chk("Hydrogen Sensors / Monitoring", "h2_sensors")
            with c3:
                chk("Operating Procedures Updated", "operating_procedure_updated")
            with c4:
                chk("Leak Detection Enhanced", "leak_detection_enhanced")
            with c5:
                chk("Training / Competence Verified", "training_complete")

        if st.button("Save Segment Inputs"):
            r = api_post(f"/segments/{sel}/inputs", payload)
            if r.ok:
                st.success("Inputs saved.")
            else:
                st.error(r.text)

# SCORE TAB
with tabs[2]:
    st.subheader("HRI Score & Dashboard")
    st.markdown("""
**Readiness classes (HRI bands implemented in the engine):**

- 0–40 → 🔴 **Not Ready** – Major upgrades required  
- 41–69 → 🟠 **Conditionally Ready** – Limited blending (<20% H₂) only  
- 70–85 → 🟢 **Ready with Controls** – Hydrogen service with monitoring  
- 86–100 → 🔵 **Fully Ready** – Suitable for hydrogen duty  
""")

    segs = api_get("/segments")
    seg_list = [s["id"] for s in (segs.json() if segs.ok else [])]
    if not seg_list:
        st.info("Create a segment first in the Setup tab.")
    else:
        sel = st.selectbox("Select Segment to Score", seg_list, key="score_sel")
        if st.button("Compute HRI for Selected Segment"):
            r = api_post(f"/segments/{sel}/hri/compute")
            if r.ok:
                data = r.json()
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.metric("HRI Score", data["hri"], data["readiness_class"])
                with col2:
                    st.write("Pillar Scores (M, D, I, C, E, Q, O):")
                    pillar_df = pd.DataFrame(
                        {"pillar": list(data["pillars"].keys()), "score": list(data["pillars"].values())}
                    ).sort_values("pillar")
                    # Band colours (match readiness palette)
                    def band(s):
                        if s <= 0.40:
                            return "Not Ready"
                        elif s <= 0.69:
                            return "Conditionally Ready"
                        elif s <= 0.85:
                            return "Ready with Controls"
                        else:
                            return "Fully Ready"
                    pillar_df["band"] = pillar_df["score"].apply(band)
                    band_scale = alt.Scale(
                        domain=["Not Ready", "Conditionally Ready", "Ready with Controls", "Fully Ready"],
                        range=["#d73027", "#fc8d59", "#1a9850", "#4575b4"],
                    )
                    # Background bands
                    bands = pd.DataFrame(
                        {
                            "ymin": [0.00, 0.41, 0.70, 0.86],
                            "ymax": [0.40, 0.69, 0.85, 1.00],
                            "band": ["Not Ready", "Conditionally Ready", "Ready with Controls", "Fully Ready"],
                        }
                    )
                    bg = (
                        alt.Chart(bands)
                        .mark_rect(opacity=0.12)
                        .encode(
                            x=alt.value(0),
                            x2=alt.value(1),
                            y=alt.Y("ymin:Q", scale=alt.Scale(domain=[0, 1]), title="Score (0–1)"),
                            y2="ymax:Q",
                            color=alt.Color("band:N", scale=band_scale, legend=None),
                        )
                    )
                    bars = (
                        alt.Chart(pillar_df)
                        .mark_bar(size=32)
                        .encode(
                            x=alt.X("pillar:N", title="Pillar"),
                            y=alt.Y("score:Q", scale=alt.Scale(domain=[0, 1]), title="Score (0–1)"),
                            color=alt.Color("band:N", scale=band_scale, title="Band"),
                            tooltip=["pillar", alt.Tooltip("score:Q", format=".2f"), "band"],
                        )
                    )
                    rules = alt.Chart(pd.DataFrame({"y": [0.40, 0.69, 0.85]})).mark_rule(strokeDash=[4, 3]).encode(
                        y="y:Q"
                    )
                    pillar_chart = (bg + bars + rules).properties(height=320, title="Pillar Scores with Readiness Bands")
                    st.altair_chart(pillar_chart, use_container_width=True)


                # Fracture mechanics badge
                inputs_resp = api_get(f"/segments/{sel}/inputs")
                if inputs_resp.ok:
                    ins = inputs_resp.json().get("inputs", {})
                    ki = ins.get("ki_mpa_sqrtm")
                    kth = ins.get("kth_mpa_sqrtm")
                    if ki is not None and kth is not None:
                        if ki > kth:
                            st.error(
                                f"Fracture mechanics gate ACTIVE: K_I = {ki} MPa√m exceeds K_TH = {kth} MPa√m. "
                                "Metallurgy pillar and HRI have been capped."
                            )
                        else:
                            st.success(
                                f"Fracture mechanics check passed: K_I = {ki} MPa√m ≤ K_TH = {kth} MPa√m."
                            )
                    else:
                        st.info("K_I / K_TH not fully populated; fracture gate could not be fully evaluated.")

                st.markdown("**Top Drivers (including gating conditions):**")
                for d in data["drivers"]:
                    st.write("• " + d)

                st.markdown("**Narrative Recommendation:**")
                st.markdown(build_narrative(data.get("pillars", {})))

            else:
                st.error(r.text)

    st.markdown("---")
    st.subheader("Portfolio Dashboard – Latest Scores & Mini Heatmap")
    latest = api_get("/scores/latest")
    if latest.ok:
        df = pd.DataFrame(latest.json())
        if not df.empty:
            st.dataframe(df, use_container_width=True)
            df_hm = df.dropna(subset=["hri"]).copy()
            if not df_hm.empty:
                df_hm["mid_km"] = 0.5 * (df_hm["start_km"] + df_hm["end_km"])
                color_scale = alt.Scale(
                    domain=["Not Ready", "Conditionally Ready", "Ready with Controls", "Fully Ready"],
                    range=["#d73027", "#fc8d59", "#1a9850", "#4575b4"],
                )
                heatmap = (
                    alt.Chart(df_hm)
                    .mark_rect(stroke="white", strokeWidth=1)
                    .encode(
                        x=alt.X("start_km:Q", title="Start km"),
                        x2="end_km:Q",
                        y=alt.Y("pipeline_id:N", title="Pipeline"),
                        color=alt.Color("readiness_class:N", scale=color_scale, title="Class"),
                        tooltip=["pipeline_id", "segment_id", "start_km", "end_km", "hri", "readiness_class"],
                    )
                    .properties(height=max(240, 70 * df_hm["pipeline_id"].nunique()), title="Segment Readiness Heatmap (visible)")
                )
                st.altair_chart(heatmap, use_container_width=True)
        else:
            st.info("No scores computed yet.")
    else:
        st.error(latest.text)
