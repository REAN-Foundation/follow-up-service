import json
from fastapi import APIRouter, Depends, HTTPException, Path, status, File, UploadFile
from fastapi.responses import JSONResponse
import shutil
import os
from app.common.base_response import BaseResponseModel
from app.common.response_model import ResponseModel
from app.common.utils import get_temp_filepath
from .test_handler import handle,readfile,updatefile,update_whatsappid,update_reply_by_ph,readfile_summary,readfile_content_by_phone

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

@router.get("/gmu/appointment-status/{phone_number}/days/{date_string}", status_code=status.HTTP_200_OK)
async def read_file(phone_number: str, date_string: str):
    ph_number = (f"+{phone_number}")
    number = ph_number.replace(' ', '')
    file_name=(f"gmu_followup_file{date_string}.json")
    filename = file_name.replace(' ', '')
    file_path = get_temp_filepath(filename)
    try:
        return await readfile_content_by_phone(file_path,number)
    except Exception as e:
        print(e)
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": "Internal Server Error"})

@router.get("/gmu/status-report/{date_str}", status_code=status.HTTP_200_OK)
async def read_file(date_str: str):
    file_name=(f"gmu_followup_file{date_str}.json")
    filename = file_name.replace(' ', '')
    file_path = get_temp_filepath(filename)
    try:
        appointment_followup_data = await readfile(file_path)        
        followup_summary = await readfile_summary(file_path,filename)
        # followup_data = json.loads(appointment_followup_data)
        # summary = json.loads(followup_summary)
        data = {
            "file_data":appointment_followup_data,
            "summary":followup_summary 
            } 
        return(data)
    except Exception as e:
        print(e)
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": "Internal Server Error"})

@router.put("/gmu/appointment-status-update/{phone_number}/days/{date_str}",  status_code=status.HTTP_201_CREATED)
async def update_reply_whatsappid_by_ph(phone_number: str, new_data: dict, date_str: str):
    try:
        print(phone_number)
        ph_number = (f"+{phone_number}")
        number = ph_number.replace(' ', '')
        file_name=(f"gmu_followup_file{date_str}.json")
        filename = file_name.replace(' ', '')
        file_path = get_temp_filepath(filename)
        content = new_data
        updated_data = await update_reply_by_ph(file_path, number, content)
        return updated_data
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

########################################################################
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

