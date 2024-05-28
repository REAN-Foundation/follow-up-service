import json
from fastapi import APIRouter, Depends, HTTPException, Path, status, File, UploadFile
from fastapi.responses import JSONResponse
import shutil
import os
from app.common.base_response import BaseResponseModel
from app.common.response_model import ResponseModel
from app.common.utils import  find_recent_file_with_prefix, get_temp_filepath
from .appointment_test_handler import handle, read_appointment_file,update_reply_by_ph,readfile_summary,readfile_content_by_phone
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
async def test(file: UploadFile = File(...)):
    try:
        return await handle(file)
    except Exception as e:
        print(e)
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": "Internal Server Error"})

@router.get("/gmu/appointment-status/{phone_number}/days/{date_string}", status_code=status.HTTP_200_OK)
async def read_file(phone_number: str, date_string: str):
    ph_number = (f"+{phone_number}")
    number = ph_number.replace(' ', '')
    file_name=(f"gmu_followup_file_{date_string}.json")
    filename = file_name.replace(' ', '')
    # file_path = get_temp_filepath(filename)
    try:
        return await readfile_content_by_phone(filename,number)
    except Exception as e:
        print(e)
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": "Internal Server Error"})

@router.get("/gmu/status-report/{date_str}", status_code=status.HTTP_200_OK)
async def read_file(date_str: str):
    file_name=(f"gmu_followup_file_{date_str}.json")
    filename = file_name.replace(' ', '')
    # file_path = get_temp_filepath(filename)
    try:
        appointment_followup_data = await read_appointment_file(filename)        
        followup_summary = await readfile_summary(filename)
        data = {
            "File_data":appointment_followup_data,
            "Summary":followup_summary 
            } 
        return(data)
    except Exception as e:
        print(e)
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": "Internal Server Error"})

@router.put("/gmu/appointment-status/{phone_number}/days/{date_str}",  status_code=status.HTTP_201_CREATED)
async def update_reply_whatsappid_by_ph(phone_number: str, new_data: dict, date_str: str):
    try:
        print(phone_number)
        ph_number = (f"+{phone_number}")
        number = ph_number.replace(' ', '')
        file_name=(f"gmu_followup_file_{date_str}.json")
        filename = file_name.replace(' ', '')
        # file_path = get_temp_filepath(filename)
        content = new_data
        updated_data = await update_reply_by_ph(filename, number, content)
        return updated_data
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/gmu/recent-status-report/recent-file", status_code=status.HTTP_200_OK)
async def read_file():
    # code to get recent file in cache
    # filename = cache.get('recent_file')
    # print(" RECENT FILE:",filename)
    
    # code to get recent file from dir list created at timestamp
    folder_path = os.path.join(os.getcwd(), "temp")
    prefix = "gmu_followup_file_"
    filename =find_recent_file_with_prefix(folder_path, prefix)
    
    print(filename)
    file_path = get_temp_filepath(filename)
    try:
        appointment_followup_data = await read_appointment_file(file_path)        
        followup_summary = await readfile_summary(file_path,filename)
        data = {
            "File_data":appointment_followup_data,
            "Summary":followup_summary 
            } 
        return(data)
    except Exception as e:
        print(e)
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": "Internal Server Error"})
