from fastapi import FastAPI
from api.routers import kpi_api, health_api

app = FastAPI(title="KPI Anomaly Detection")

app.include_router(kpi_api.router)
app.include_router(health_api.router)
