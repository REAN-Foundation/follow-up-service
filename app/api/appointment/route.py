import os
from fastapi import APIRouter, HTTPException, status
from fastapi import Request
from fastapi.responses import JSONResponse
from app.api.appointment.handler import handle, handle_aws, read_appointment_file, readfile_content, readfile_content_by_phone, readfile_summary, recent_file, update_reply_by_ph
from app.common.appointment_api.appointment_utils import form_file_name
from app.common.base_response import BaseResponseModel
from app.common.cache import cache
from fastapi import FastAPI, Depends
from app.common.response_model import ResponseModel
from app.common.utils import format_date_, format_phone_number
from app.dependency import get_storage_service
from app.interfaces.appointment_storage_interface import IStorageService
from fastapi import APIRouter, Depends, HTTPException, Path, status, File, UploadFile

# client_bot_name = os.getenv("GGHN_BOT_CLIENT_NAME")
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
        in_date = date_string
        d_str = in_date.split('-')
        if(d_str[0].startswith('0') or d_str[2].startswith('0')):
            datefirst = int(d_str[0])
            datelast =  int(d_str[2])
            date_str = (f"{datefirst}-{d_str[1]}-{datelast}")
        else: 
            date_str = date_string 
               
        print("formated_date...",date_str)
        response = await readfile_content(date_str,storage_service)
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
                return await handle(storage_service,file)
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
        in_date = date_str
        client = (client_bot_name[0]).lower()
        print("client name--",client)
        date_str = await format_date_(in_date)
        if(date_str == 'None'):
            print("date returned null")
        
        print("formated_date...",date_str)
        number = await format_phone_number(phone_number)
        if(number == 'None'):
            print("number returned null")
        filename = await form_file_name(client,date_str)
        if(filename == 'None'):
            print("filename returned null")
        content = new_data
        updated_data = await update_reply_by_ph(filename, number, content,storage_service)
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
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": "Recent file error"})

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
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": "Internal Server Error"})

    
@router.get("/{client_bot_name}/appointment-status/{phone_number}/days/{date_string}", status_code=status.HTTP_200_OK)
async def read_individual_phone_data(client_bot_name: str, phone_number: str, date_string: str,storage_service: IStorageService  = Depends(get_storage_service)):
    try:
        client = (client_bot_name[0]).lower()
        date_str = await format_date_(date_string)
        if(date_str == 'None'):
            print("date returned null")
        number = await format_phone_number(phone_number)
        if(number == 'None'):
            print("number returned null")
        filename = await form_file_name(client,date_str)
        if(filename == 'None'):
            print("filename returned null")

        return await readfile_content_by_phone(filename,number,storage_service)
    except Exception as e:
        print(e)
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": "Internal Server Error"})
