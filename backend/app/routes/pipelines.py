from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Pipeline
from app.schemas import PipelineCreate

router=APIRouter()

@router.post("")
def create_pipeline(payload:PipelineCreate,db:Session=Depends(get_db)):
    if db.get(Pipeline,payload.id):
        raise HTTPException(status_code=400,detail="Pipeline already exists")
    p=Pipeline(**payload.model_dump())
    db.add(p); db.commit()
    return {"ok":True,"pipeline_id":p.id}

@router.get("")
def list_pipelines(db:Session=Depends(get_db)):
    pipes=db.query(Pipeline).all()
    return [{"id":p.id,"name":p.name,"operator":p.operator,"region":p.region} for p in pipes]
