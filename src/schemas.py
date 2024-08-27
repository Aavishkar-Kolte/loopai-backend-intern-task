from pydantic import BaseModel

class ReportRequest(BaseModel):
    report_id: str

class ReportResponse(BaseModel):
    status: str
    report: str = None
