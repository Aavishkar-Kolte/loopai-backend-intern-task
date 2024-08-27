from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import StoreStatus
from ..schemas import ReportRequest, ReportResponse

router = APIRouter()

reports = {}

@router.get("/store_ids", response_model=ReportResponse)
def store_ids(db: Session = Depends(get_db)):
    data = db.query(StoreStatus.store_id).distinct().all()
    arr_data = [str(d[0]) for d in data]  # Convert integers to strings
    str_data = ", ".join(arr_data)
    return {"status": "done", "report": str_data}