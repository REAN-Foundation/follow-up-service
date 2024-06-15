import os
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi import Request
from fastapi.responses import JSONResponse

from app.api.appointment.gmu.appointment_handler import handle, read_appointment_file, readfile_content_by_phone, readfile_summary, recent_file, update_reply_by_ph
from app.common.cache import cache
from app.dependency import get_storage_service
from app.interfaces.appointment_storage_interface import IStorageService

###############################################################################

router = APIRouter(
    prefix="/appointment-schedules/gmu",
    tags=["appointment-schedules", "gmu"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)

###############################################################################

@router.post("/upload")
async def handle_sns_notification(message: Request,storage_service: IStorageService = Depends(get_storage_service)):
    try:
        print("Notification received")
        result = await handle(message,storage_service)
        return JSONResponse(content=result)
    except Exception as e:
        print(e)
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": "Internal Server Error"})


@router.get("/appointment-status/{phone_number}/days/{date_string}", status_code=status.HTTP_200_OK)
async def read_file(phone_number: str, date_string: str,storage_service: IStorageService  = Depends(get_storage_service)):
    ph_number = (f"+{phone_number}")
    number = ph_number.replace(' ', '')
    file_name=(f"gmu_followup_file_{date_string}.json")
    filename = file_name.replace(' ', '')
    
    try:
        return await readfile_content_by_phone(filename,number,storage_service)
    except Exception as e:
        print(e)
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": "Internal Server Error"})

@router.get("/status-report/{date_str}", status_code=status.HTTP_200_OK)
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

@router.put("/appointment-status/{phone_number}/days/{date_str}",  status_code=status.HTTP_201_CREATED)
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


@router.get("/recent-status-report/recent-file", status_code=status.HTTP_200_OK)
async def read_file(storage_service: IStorageService = Depends(get_storage_service)):
    file_prefix = "gmu_followup_file_"
    filename = await recent_file(file_prefix,storage_service)
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

