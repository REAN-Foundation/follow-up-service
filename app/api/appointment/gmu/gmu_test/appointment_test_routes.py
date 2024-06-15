import json
from fastapi import APIRouter, Depends, HTTPException, Path, status, File, UploadFile
from fastapi.responses import JSONResponse
import shutil
import os
# from app.common.appointment.appointment_utils import find_recent_file_from_atlas
from app.common.base_response import BaseResponseModel
from app.common.response_model import ResponseModel
from app.common.utils import get_temp_filepath
from app.dependency import get_storage_service
from app.interfaces.appointment_storage_interface import IStorageService
from .appointment_test_handler import handle, read_appointment_file, recent_file,update_reply_by_ph,readfile_summary,readfile_content_by_phone
from app.common.cache import cache
###############################################################################

router = APIRouter(
    prefix="/appointments/tests",
    tags=["tests"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)

###############################################################################

# Test route

@router.post("/upload", status_code=status.HTTP_201_CREATED, response_model=ResponseModel[BaseResponseModel|None])
async def test(file: UploadFile = File(...),storage_service: IStorageService = Depends(get_storage_service)):
    try:
        return await handle(storage_service,file)
    except Exception as e:
        print(e)
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": "Internal Server Error"})

@router.get("/gmu/appointment-status/{phone_number}/days/{date_string}", status_code=status.HTTP_200_OK)
async def read_file(phone_number: str, date_string: str,storage_service: IStorageService = Depends(get_storage_service)):
    ph_number = (f"+{phone_number}")
    number = ph_number.replace(' ', '')
    file_name=(f"gmu_followup_file_{date_string}.json")
    filename = file_name.replace(' ', '')
    
    try:
        return await readfile_content_by_phone(filename,number,storage_service)
    except Exception as e:
        print(e)
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": "Internal Server Error"})

@router.get("/gmu/status-report/{date_str}", status_code=status.HTTP_200_OK)
async def read_file(date_str: str,storage_service: IStorageService = Depends(get_storage_service)):
    file_name=(f"gmu_followup_file_{date_str}.json")
    filename = file_name.replace(' ', '')
    
    try:
        appointment_followup_data = await read_appointment_file(filename,storage_service)        
        followup_summary = await readfile_summary(filename,storage_service)
        data = {
            "File_data":appointment_followup_data,
            "Summary":followup_summary 
            } 
        return(data)
    except Exception as e:
        print(e)
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": "Internal Server Error"})

@router.put("/gmu/appointment-status/{phone_number}/days/{date_str}",  status_code=status.HTTP_201_CREATED)
async def update_reply_whatsappid_by_ph(phone_number: str, new_data: dict, date_str: str,storage_service: IStorageService = Depends(get_storage_service)):
    try:
        print(phone_number)
        ph_number = (f"+{phone_number}")
        number = ph_number.replace(' ', '')
        file_name=(f"gmu_followup_file_{date_str}.json")
        filename = file_name.replace(' ', '')
       
        content = new_data
        updated_data = await update_reply_by_ph(filename, number, content,storage_service)
        return updated_data
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/gmu/recent-status-report/recent-file", status_code=status.HTTP_200_OK)
async def read_file(storage_service: IStorageService = Depends(get_storage_service)):
    file_prefix = "gmu_followup_file_"
    filename =  await recent_file(file_prefix,storage_service)
    print(filename)
      
    try:
        appointment_followup_data = await read_appointment_file(filename,storage_service)        
        followup_summary = await readfile_summary(filename,storage_service)
        data = {
            "File_data":appointment_followup_data,
            "Summary":followup_summary 
            } 
        return(data)
    except Exception as e:
        print(e)
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": "Internal Server Error"})
