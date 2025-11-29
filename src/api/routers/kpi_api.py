from pydantic import BaseModel
from typing import List, Dict, Any
from fastapi import APIRouter

# from shared.train import train_kpi
# from shared.detect import detect_kpi

router = APIRouter(prefix="/kpi", tags=["kpi"])


class KPIData(BaseModel):
    data: List[Dict[str, Any]]


@router.post("/detect/{kpi_name}")
def detect(kpi_name: str, payload: KPIData):
    result = detect_kpi(kpi_name, payload.data)
    return {"result": result}


@router.post("/train/{kpi_name}")
def train(kpi_name: str):
    train_kpi(kpi_name)
    return {"status": "training started"}
