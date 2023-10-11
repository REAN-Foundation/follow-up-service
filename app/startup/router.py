from fastapi import APIRouter, Depends, HTTPException, status
from app.api.api_router import router as api_router
import os

PORT = os.environ.get("PORT", 3000)
SERVICE_NAME = os.environ.get("SERVICE_NAME", "Reminder Service")

router = APIRouter()

@router.get('/', status_code=200)
def service_info():
    return "{service} is running on port {port}".format(service=SERVICE_NAME, port=PORT)

@router.get('/health-check', status_code=200)
def perform_healthcheck():
    return "OK"

# Add API outer here...
router.include_router(api_router)
