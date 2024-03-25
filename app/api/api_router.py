from fastapi import APIRouter
from .appointment.appointment_routes import router as appointment_router
from .test.appointment_test_routes import router as test_router
from .gghndb_appointment.gghndb_router import router as gghn_router
import os

API_PREFIX = os.environ.get("API_PREFIX", "/api/v1")

router = APIRouter(prefix=API_PREFIX)

def add_routes():
    router.include_router(appointment_router)
    router.include_router(test_router)
    router.include_router(gghn_router)
    # Add other routes here

add_routes()
