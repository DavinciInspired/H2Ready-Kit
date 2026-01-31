from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Segment,Pipeline,SegmentInputs
from app.schemas import SegmentCreate,SegmentInputsUpsert

router=APIRouter()

@router.post("")
def create_segment(payload:SegmentCreate,db:Session=Depends(get_db)):
    if not db.get(Pipeline,payload.pipeline_id):
        raise HTTPException(status_code=404,detail="Pipeline not found")
    if db.get(Segment,payload.id):
        raise HTTPException(status_code=400,detail="Segment already exists")
    s=Segment(**payload.model_dump())
    db.add(s); db.add(SegmentInputs(segment_id=s.id)); db.commit()
    return {"ok":True,"segment_id":s.id}

@router.get("")
def list_segments(pipeline_id:str|None=None,db:Session=Depends(get_db)):
    q=db.query(Segment)
    if pipeline_id:
        q=q.filter(Segment.pipeline_id==pipeline_id)
    segs=q.all()
    return [{"id":s.id,"pipeline_id":s.pipeline_id,"start_km":s.start_km,"end_km":s.end_km} for s in segs]

@router.get("/{segment_id}/inputs")
def get_inputs(segment_id:str,db:Session=Depends(get_db)):
    seg=db.get(Segment,segment_id)
    if not seg:
        raise HTTPException(status_code=404,detail="Segment not found")
    inp=db.get(SegmentInputs,segment_id)
    if not inp:
        inp=SegmentInputs(segment_id=segment_id); db.add(inp); db.commit(); db.refresh(inp)
    data={c.name:getattr(inp,c.name) for c in inp.__table__.columns}
    return {"segment_id":segment_id,"inputs":data}

@router.post("/{segment_id}/inputs")
def upsert_inputs(segment_id:str,payload:SegmentInputsUpsert,db:Session=Depends(get_db)):
    if not db.get(Segment,segment_id):
        raise HTTPException(status_code=404,detail="Segment not found")
    inp=db.get(SegmentInputs,segment_id)
    if not inp:
        inp=SegmentInputs(segment_id=segment_id); db.add(inp)
    for k,v in payload.model_dump().items():
        setattr(inp,k,v)
    db.commit()
    return {"ok":True}
