from datetime import datetime
import os
from fastapi import APIRouter, HTTPException, status
from fastapi import Request
from fastapi.responses import JSONResponse
from app.api.appointment.handler import handle, handle_aws, read_appointment_file, readfile_content, readfile_content_by_phone, readfile_summary, recent_file, update_reply_by_ph
from app.common.appointment_api.appointment_utils import form_file_name, get_client_name
from app.common.base_response import BaseResponseModel
from app.common.cache import cache
from fastapi import FastAPI, Depends
from app.common.response_model import ResponseModel
from app.common.schedule_params import ScheduleParams
from app.common.utils import format_date_, format_phone_number
from app.dependency import get_storage_service
from app.interfaces.appointment_storage_interface import IStorageService
from fastapi import APIRouter, Depends, HTTPException, Path, status, File, UploadFile

from scheduler import schedule_job

##################################################################################
router = APIRouter(
 
    prefix="/appointment-schedules",
    tags=["appointment-schedules"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)
#################################################################################
@router.post("/{client}/set-reminders/date/{date_string}", status_code=status.HTTP_201_CREATED,response_model=ResponseModel[BaseResponseModel|None])
async def read_file(client: str, date_string: str,storage_service: IStorageService = Depends(get_storage_service)):
    try:
        response = await readfile_content(client, date_string, storage_service)
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
    
@router.post("/tests/upload", status_code=status.HTTP_201_CREATED, response_model=ResponseModel[BaseResponseModel|None])
async def test(file: UploadFile = File(...),storage_service: IStorageService = Depends(get_storage_service)):
            try:
               result = await handle(storage_service,file)
               return JSONResponse(content=result)
            except Exception as e:
                print(e)
                return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": "Internal Server Error"})
            
@router.post("/upload")
async def handle_sns_notification(message: Request,storage_service: IStorageService = Depends(get_storage_service)):
    try:
        print("Notification received")
        result = await handle_aws(message,storage_service)
        return JSONResponse(content=result)
    except Exception as e:
        print(e)
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": "Internal Server Error"})
    
@router.put("/{client_bot_name}/appointment-status/{phone_number}/days/{date_str}",  status_code=status.HTTP_201_CREATED)
async def update_reply_and_whatsappid_by_ph(client_bot_name: str, phone_number: str, new_data: dict, date_str: str,storage_service:IStorageService = Depends(get_storage_service)):
    try:
        content = new_data
        updated_data = await update_reply_by_ph(client_bot_name,date_str, phone_number, content,storage_service)
        return {
            "Message" : "Updated response successfully",
            "Data" : updated_data
        } 
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    
@router.get("/{client}/recent-status-report/recent-file", status_code=status.HTTP_200_OK)
async def read_recent_file(client: str,storage_service: IStorageService = Depends(get_storage_service)): 
    file_prefix = (f"{client}_appointment_").lower()
    filename = await recent_file(file_prefix,storage_service)
    print(filename)

    try:
        followup_data = await read_appointment_file(filename,storage_service)        
        followup_summary = await readfile_summary(filename,storage_service)
        data = {
            "Summary":followup_summary,
            "File_data":followup_data,
            } 
        return(data)
    except Exception as e:
        print(e)
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"message": "File not found"})

@router.get("/{client}/status-report/{date_str}", status_code=status.HTTP_200_OK)
async def status_for_date_file(client: str,date_str: str,storage_service: IStorageService = Depends(get_storage_service)):
    date_string = await format_date_(date_str)
    if(date_string == 'None'):
        print("date returned null")
    filename = await form_file_name(client,date_string)
    if(filename == 'None'):
        print("filename returned null")
   
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
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"message": "File not found"})

    
@router.get("/{client_bot_name}/appointment-status/{phone_number}/days/{date_string}", status_code=status.HTTP_200_OK)
async def read_individual_phone_data(client_bot_name: str, phone_number: str, date_string: str,storage_service: IStorageService  = Depends(get_storage_service)):
    try:
        return await readfile_content_by_phone(client_bot_name, phone_number,date_string,storage_service)
    except Exception as e:
        print(e)
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": "Internal Server Error"})

@router.post("/{client}/schedule")
async def schedule_job_endpoint(client: str, params: ScheduleParams):
    try:
        print("printing date",params.date)
        print(params.time)
        # Combine date and time
        for i in params.date:
            schedule_datetime = f"{i} {params.time}"
            schedule_datetime = datetime.strptime(schedule_datetime, "%Y-%m-%d %H:%M")
            print(schedule_datetime)
        # Schedule the job
            schedule_job(schedule_datetime)

        return {"message": "Job scheduled successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))