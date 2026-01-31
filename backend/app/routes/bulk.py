from fastapi import APIRouter
router=APIRouter()
@router.get("/bulk/template")
def template():
    return {"columns":[]}
