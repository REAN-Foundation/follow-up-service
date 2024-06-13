# from fastapi import APIRouter
# from .appointment_local.gmu_local.appointment_local_routes import router as appointment_router
# from .appointment_local.gmu_local.gmu_test_local.appointment_test_local_routes import router as test_router
# from .appointment_local.gghn_local.gghndb_local_router import router as gghn_router
# import os

from fastapi import APIRouter
from .appointment.gmu.appointment_routes import router as appointment_router
from .appointment.gmu.gmu_test.appointment_test_routes import router as test_router
from .appointment.gghn.gghndb_router import router as gghn_router
import os


API_PREFIX = os.environ.get("API_PREFIX", "/api/v1")

router = APIRouter(prefix=API_PREFIX)

def add_routes():
    router.include_router(appointment_router)
    router.include_router(test_router)
    router.include_router(gghn_router)
    # Add other routes here

add_routes()
