from pydantic import BaseModel
from typing import Optional,Dict,List

class PipelineCreate(BaseModel):
    id:str
    name:str
    operator:Optional[str]=None
    region:Optional[str]=None

class SegmentCreate(BaseModel):
    id:str
    pipeline_id:str
    start_km:float
    end_km:float

class SegmentInputsUpsert(BaseModel):
    api_grade:Optional[str]=None
    smys_mpa:Optional[float]=None
    yt_ratio:Optional[float]=None
    hardness_haz_hv:Optional[float]=None
    seam_type:Optional[str]=None
    ki_mpa_sqrtm:Optional[float]=None
    kth_mpa_sqrtm:Optional[float]=None
    stress_ratio:Optional[float]=None
    cycles_per_day:Optional[float]=None
    cycle_range_bar:Optional[float]=None
    surge_events_per_year:Optional[float]=None
    dpdt_p95_bar_per_s:Optional[float]=None
    temp_min_c:Optional[float]=None
    temp_max_c:Optional[float]=None
    max_metal_loss_pct:Optional[float]=None
    crack_density_per_km:Optional[float]=None
    max_crack_length_mm:Optional[float]=None
    repair_backlog_high:Optional[bool]=None
    coating_type:Optional[str]=None
    coating_age_years:Optional[float]=None
    dcvg_anomaly_pct:Optional[float]=None
    cp_potential_avg_v:Optional[float]=None
    cp_overprotect_pct:Optional[float]=None
    soil_resistivity_ohm_cm:Optional[float]=None
    soil_ph:Optional[float]=None
    mic_risk:Optional[str]=None
    moisture_high:Optional[bool]=None
    stray_current_risk:Optional[str]=None
    ili_coverage_pct:Optional[float]=None
    cp_survey_age_months:Optional[float]=None
    scada_uptime_pct:Optional[float]=None
    missing_fields_pct:Optional[float]=None
    has_h2_plan:Optional[bool]=None
    h2_sensors:Optional[bool]=None
    operating_procedure_updated:Optional[bool]=None
    leak_detection_enhanced:Optional[bool]=None
    training_complete:Optional[bool]=None

class ScoreOut(BaseModel):
    segment_id:str
    model_version:str
    hri:float
    readiness_class:str
    pillars:Dict[str,float]
    weights:Dict[str,float]
    drivers:List[str]

class BulkUpsertResult(BaseModel):
    pipelines_created:int
    segments_created:int
    inputs_upserted:int
    rows_processed:int
    errors:List[str]
