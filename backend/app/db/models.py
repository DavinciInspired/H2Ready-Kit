from sqlalchemy import Column,String,Float,Integer,DateTime,ForeignKey,Boolean,Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class Pipeline(Base):
    __tablename__="pipelines"
    id=Column(String,primary_key=True)
    name=Column(String,nullable=False)
    operator=Column(String)
    region=Column(String)
    created_at=Column(DateTime(timezone=True),server_default=func.now())
    segments=relationship("Segment",back_populates="pipeline",cascade="all, delete-orphan")

class Segment(Base):
    __tablename__="segments"
    id=Column(String,primary_key=True)
    pipeline_id=Column(String,ForeignKey("pipelines.id"),nullable=False)
    start_km=Column(Float,nullable=False)
    end_km=Column(Float,nullable=False)
    pipeline=relationship("Pipeline",back_populates="segments")
    inputs=relationship("SegmentInputs",back_populates="segment",uselist=False,cascade="all, delete-orphan")
    scores=relationship("HRIScore",back_populates="segment",cascade="all, delete-orphan")

class SegmentInputs(Base):
    __tablename__="segment_inputs"
    segment_id=Column(String,ForeignKey("segments.id"),primary_key=True)

    # Metallurgy
    api_grade=Column(String)
    smys_mpa=Column(Float)
    yt_ratio=Column(Float)
    hardness_haz_hv=Column(Float)
    seam_type=Column(String)
    ki_mpa_sqrtm=Column(Float)
    kth_mpa_sqrtm=Column(Float)

    # Design & Ops
    stress_ratio=Column(Float)
    cycles_per_day=Column(Float)
    cycle_range_bar=Column(Float)
    surge_events_per_year=Column(Float)
    dpdt_p95_bar_per_s=Column(Float)
    temp_min_c=Column(Float)
    temp_max_c=Column(Float)

    # Integrity
    max_metal_loss_pct=Column(Float)
    crack_density_per_km=Column(Float)
    max_crack_length_mm=Column(Float)
    repair_backlog_high=Column(Boolean)

    # Coating & CP
    coating_type=Column(String)
    coating_age_years=Column(Float)
    dcvg_anomaly_pct=Column(Float)
    cp_potential_avg_v=Column(Float)
    cp_overprotect_pct=Column(Float)

    # Environment
    soil_resistivity_ohm_cm=Column(Float)
    soil_ph=Column(Float)
    mic_risk=Column(String)
    moisture_high=Column(Boolean)
    stray_current_risk=Column(String)

    # Data Quality
    ili_coverage_pct=Column(Float)
    cp_survey_age_months=Column(Float)
    scada_uptime_pct=Column(Float)
    missing_fields_pct=Column(Float)

    # Operational Controls
    has_h2_plan=Column(Boolean)
    h2_sensors=Column(Boolean)
    operating_procedure_updated=Column(Boolean)
    leak_detection_enhanced=Column(Boolean)
    training_complete=Column(Boolean)

    segment=relationship("Segment",back_populates="inputs")

class HRIScore(Base):
    __tablename__="hri_scores"
    id=Column(Integer,primary_key=True,autoincrement=True)
    segment_id=Column(String,ForeignKey("segments.id"),nullable=False)
    model_version=Column(String,nullable=False,default="rules-v2-gated")
    hri=Column(Float,nullable=False)
    readiness_class=Column(String,nullable=False)
    m=Column(Float,nullable=False)
    d=Column(Float,nullable=False)
    i=Column(Float,nullable=False)
    c=Column(Float,nullable=False)
    e=Column(Float,nullable=False)
    q=Column(Float,nullable=False)
    o=Column(Float,nullable=False)
    drivers_json=Column(Text)
    created_at=Column(DateTime(timezone=True),server_default=func.now())
    segment=relationship("Segment",back_populates="scores")
