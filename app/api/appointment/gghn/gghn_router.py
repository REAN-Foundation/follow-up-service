import os
from fastapi import APIRouter, HTTPException, status
from fastapi import Request
from fastapi.responses import JSONResponse
from app.common.base_response import BaseResponseModel
from app.common.cache import cache
from app.api.appointment.gghn.gghn_handler import read_appointment_file, readfile_content, readfile_summary, recent_file, update_gghn_reply_by_ph
from app.common.response_model import ResponseModel
from fastapi import FastAPI, Depends
from app.dependency import get_storage_service
from app.interfaces.appointment_storage_interface import IStorageService

client_bot_name = os.getenv("GGHN_BOT_CLIENT_NAME")
##################################################################################
router = APIRouter(
 
    prefix=f"/appointment-schedules/{client_bot_name}",
    tags=["appointment-schedules", "gghn"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)
#################################################################################
@router.post("/set-reminders/date/{date_string}", status_code=status.HTTP_201_CREATED,response_model=ResponseModel[BaseResponseModel|None])
async def read_file(date_string: str,storage_service: IStorageService = Depends(get_storage_service)):
    try:
        response = await readfile_content(date_string,storage_service)
        if(response == None):
            return{
                "Message":"No Appointments available",
                "Data":response 
            }
        return {
            "Message" : "Reminders created successfully",
            "Data" : response
        } 
    except Exception as e:
        print(e)
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": "Internal Server Error"})

     
@router.put("/appointment-status/{phone_number}/days/{date_str}",  status_code=status.HTTP_201_CREATED)
async def update_reply_and_whatsappid_by_ph(phone_number: str, new_data: dict, date_str: str,storage_service:IStorageService = Depends(get_storage_service)):
    try:
        print(phone_number)
        ph_number = (f"+{phone_number}")
        number = ph_number.replace(' ', '')
        file_name=(f"gghn_appointment_{date_str}.json")
        filename = file_name.replace(' ', '')
     
        content = new_data
        updated_data = await update_gghn_reply_by_ph(filename, number, content,storage_service)
        return {
            "Message" : "Updated response successfully",
            "Data" : updated_data
        } 
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    
@router.get("/recent-status-report/recent-file", status_code=status.HTTP_200_OK)
async def read_file(storage_service: IStorageService = Depends(get_storage_service)):
    file_prefix = "gghn_appointment_"
    filename = await recent_file(file_prefix,storage_service)
    print(filename)

    try:
        gghn_appointment_followup_data = await read_appointment_file(filename,storage_service)        
        followup_summary = await readfile_summary(filename,storage_service)
        data = {
            "Summary":followup_summary,
            "File_data":gghn_appointment_followup_data,
            } 
        return(data)
    except Exception as e:
        print(e)
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": "Recent file error"})

@router.get("/status-report/{date_str}", status_code=status.HTTP_200_OK)
async def read_file(date_str: str,storage_service: IStorageService = Depends(get_storage_service)):
    file_name=(f"gghn_appointment_{date_str}.json")
    filename = file_name.replace(' ', '')
   
    try:
        appointment_followup_data = await read_appointment_file(filename,storage_service)        
        followup_summary = await readfile_summary(filename,storage_service)
        data = {
            "Summary":followup_summary,
            "File_data":appointment_followup_data
            } 
        return(data)
    except Exception as e:
        print(e)
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": "Internal Server Error"})