import json
from fastapi import APIRouter, Depends, HTTPException, Path, status, File, UploadFile
from fastapi.responses import JSONResponse
import shutil
import os
from app.common.base_response import BaseResponseModel
from app.common.response_model import ResponseModel
from app.common.utils import get_temp_filepath
from .test_handler import handle,readfile,updatefile,update_whatsappid,update_reply_by_ph,readfile_summary

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

@router.get("/read_file/{filename}", status_code=status.HTTP_200_OK)
async def read_file(filename: str):
    file_path = get_temp_filepath(filename)
    try:
        return await readfile(file_path)
    except Exception as e:
        print(e)
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": "Internal Server Error"})

@router.get("/file_summary/{filename}", status_code=status.HTTP_200_OK)
async def read_file(filename: str):
    file_path = get_temp_filepath(filename)
    try:
        return await readfile_summary(file_path,filename)
    except Exception as e:
        print(e)
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": "Internal Server Error"})

@router.put("/update-content/{file_name}")
async def update_content(patient_userid: str, new_data: dict, file_name: str):
    try:
        file_path = get_temp_filepath(file_name)
        content = new_data
        updated_data = await updatefile(file_path,patient_userid, content)
        return updated_data
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    
@router.put("/WhatsAppId-update/{file_name}")
async def update_whatsapp_id(phone_number: str, new_data: dict, file_name: str):
    try:
        file_path = get_temp_filepath(file_name)
        content = new_data
        updated_data = await update_whatsappid(file_path,phone_number, content)
        return updated_data
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.put("/reply-update/{file_name}")
async def update_whatsapp_id(phone_number: str, new_data: dict, file_name: str):
    try:
        file_path = get_temp_filepath(file_name)
        content = new_data
        updated_data = await update_reply_by_ph(file_path,phone_number, content)
        return updated_data
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))