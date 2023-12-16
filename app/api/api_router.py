from fastapi import APIRouter
from .sns.appointment_routes import router as sns_router
from .test.test_routes import router as test_router
import os

API_PREFIX = os.environ.get("API_PREFIX", "/api/v1")

router = APIRouter(prefix=API_PREFIX)

def add_routes():
    router.include_router(sns_router)
    router.include_router(test_router)

    # Add other routes here

add_routes()
