from fastapi import APIRouter, Depends, status, File, UploadFile
from fastapi.responses import JSONResponse
import shutil
import os
from app.common.base_response import BaseResponseModel
from app.common.response_model import ResponseModel
from .test_handler import handle

###############################################################################

router = APIRouter(
    prefix="/tests",
    tags=["tests"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)

###############################################################################

# Test route

@router.post("/upload", status_code=status.HTTP_201_CREATED, response_model=ResponseModel[BaseResponseModel|None])
async def test(file: UploadFile = File(...)):
    try:
        return await handle(file)
    except Exception as e:
        print(e)
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": "Internal Server Error"})
