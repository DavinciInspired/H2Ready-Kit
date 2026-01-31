import json
from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Segment,SegmentInputs,HRIScore
from app.schemas import ScoreOut
from app.scoring.engine import compute_hri,WEIGHTS

router=APIRouter()

@router.post("/segments/{segment_id}/hri/compute",response_model=ScoreOut)
def compute_segment_hri(segment_id:str,db:Session=Depends(get_db)):
    if not db.get(Segment,segment_id):
        raise HTTPException(status_code=404,detail="Segment not found")
    inp=db.get(SegmentInputs,segment_id)
    if not inp:
        inp=SegmentInputs(segment_id=segment_id); db.add(inp); db.commit(); db.refresh(inp)
    inputs={c.name:getattr(inp,c.name) for c in inp.__table__.columns}
    hri,klass,pillars,drivers=compute_hri(inputs)
    rec=HRIScore(segment_id=segment_id,model_version="rules-v2-gated",
                 hri=hri,readiness_class=klass,
                 m=pillars["M"],d=pillars["D"],i=pillars["I"],c=pillars["C"],
                 e=pillars["E"],q=pillars["Q"],o=pillars["O"],
                 drivers_json=json.dumps(drivers[:80]))
    db.add(rec); db.commit()
    return ScoreOut(segment_id=segment_id,model_version=rec.model_version,
                    hri=rec.hri,readiness_class=rec.readiness_class,
                    pillars={k:float(v) for k,v in pillars.items()},
                    weights=WEIGHTS,drivers=drivers[:20])

@router.get("/scores/latest")
def latest_scores(pipeline_id:str|None=None,db:Session=Depends(get_db)):
    q=db.query(Segment)
    if pipeline_id:
        q=q.filter(Segment.pipeline_id==pipeline_id)
    segs=q.all()
    from app.db.models import HRIScore
    out=[]
    for s in segs:
        latest=(db.query(HRIScore)
                  .filter(HRIScore.segment_id==s.id)
                  .order_by(HRIScore.created_at.desc(),HRIScore.id.desc())
                  .first())
        out.append({
            "segment_id":s.id,
            "pipeline_id":s.pipeline_id,
            "start_km":s.start_km,
            "end_km":s.end_km,
            "hri":latest.hri if latest else None,
            "readiness_class":latest.readiness_class if latest else None,
            "pillars":{
                "M":latest.m,"D":latest.d,"I":latest.i,"C":latest.c,
                "E":latest.e,"Q":latest.q,"O":latest.o,
            } if latest else None,
        })
    return out
