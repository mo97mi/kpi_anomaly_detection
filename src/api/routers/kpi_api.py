from pydantic import BaseModel
from typing import List, Dict, Any
from fastapi import APIRouter, Response, HTTPException
from services.kpi_service import KPIService
from services.exceptions import KPINotFoundError

router = APIRouter(prefix="/kpi", tags=["kpi"])
kpi_service = KPIService()


class KPIData(BaseModel):
    data: List[Dict[str, Any]]


@router.post("/detect/{kpi_name}")
def detect(kpi_name: str, payload: KPIData):
    result = "detect_kpi"
    return {"result": result}


@router.post("/train/{kpi_name}")
def train(kpi_name: str):
    try:
        kpi_service.run_train(kpi_name)
        return Response(
            content="train starts", status_code=200
        )  # KPIService().run_train(kpi_name)
    except KPINotFoundError as e:
        return HTTPException(status_code=404, detail=str(e))
