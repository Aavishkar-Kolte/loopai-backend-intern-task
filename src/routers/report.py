from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import StoreStatus
from ..schemas import ReportRequest, ReportResponse, TriggerReportResponse
from ..utils import generate_report, calculate_uptime_downtime
import uuid
import os

router = APIRouter()

reports = {}

@router.post("/trigger_report", response_model=TriggerReportResponse)
def trigger_report(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    report_id = str(uuid.uuid4())
    reports[report_id] = "Running"
    background_tasks.add_task(generate_report, report_id, db, reports)
    return {"status": "Running", "report_id": report_id}



@router.get("/get_report", response_model=ReportResponse)
def get_report(report_id: str):
    if report_id not in reports:
        return {"status": "Invalid Report ID"}

    report_status = reports[report_id]

    if report_status.startswith("Failed"):
        return {"status": report_status}

    if report_status == "Running":
        return {"status": "Running"}
    else:
        try:
            with open(report_status, "r") as file:
                csv_content = file.read()
            return {"status": "Complete", "report": csv_content}
        except FileNotFoundError:
            return {"status": "Error", "message": "Report file not found"}
        except Exception as e:
            return {"status": "Error", "message": str(e)}

