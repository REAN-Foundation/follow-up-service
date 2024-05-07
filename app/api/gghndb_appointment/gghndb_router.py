import os
from fastapi import APIRouter, HTTPException, status
from fastapi import Request
from fastapi.responses import JSONResponse
from app.common.base_response import BaseResponseModel
from app.common.cache import cache
from app.api.gghndb_appointment.gghndb_handler import readfile_content
from app.common.response_model import ResponseModel
##################################################################################
router = APIRouter(
    prefix="/appointment-schedules/gghn",
    tags=["appointment-schedules", "gghn"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)
#################################################################################
@router.get("/appointment-details/date/{date_string}", status_code=status.HTTP_201_CREATED)
def read_file(date_string: str):
    try:
        return readfile_content(date_string)
    except Exception as e:
        print(e)
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": "Internal Server Error"})
        