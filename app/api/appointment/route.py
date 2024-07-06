import os
from fastapi import APIRouter, HTTPException, status
from fastapi import Request
from fastapi.responses import JSONResponse
from app.api.appointment.handler import handle, handle_aws, read_appointment_file, readfile_content, readfile_content_by_phone, readfile_summary, recent_file, update_reply_by_ph
from app.common.base_response import BaseResponseModel
from app.common.cache import cache
from fastapi import FastAPI, Depends
from app.common.response_model import ResponseModel
from app.dependency import get_storage_service
from app.interfaces.appointment_storage_interface import IStorageService
from fastapi import APIRouter, Depends, HTTPException, Path, status, File, UploadFile

client_bot_name = os.getenv("GGHN_BOT_CLIENT_NAME")
##################################################################################
router = APIRouter(
 
    prefix="/appointment-schedules",
    tags=["appointment-schedules"],
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
    
@router.put("/{client}/{client_bot_name}/appointment-status/{phone_number}/days/{date_str}",  status_code=status.HTTP_201_CREATED)
async def update_reply_and_whatsappid_by_ph(client: str, phone_number: str, new_data: dict, date_str: str,storage_service:IStorageService = Depends(get_storage_service)):
    try:
        print(phone_number)
        ph_number = (f"+{phone_number}")
        number = ph_number.replace(' ', '')
        file_name=(f"{client}_appointment_{date_str}.json")
        filename = file_name.replace(' ', '')
     
        content = new_data
        updated_data = await update_reply_by_ph(filename, number, content,storage_service)
        return {
            "Message" : "Updated response successfully",
            "Data" : updated_data
        } 
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    
@router.get("/{client}/recent-status-report/recent-file", status_code=status.HTTP_200_OK)
async def read_file(client: str,storage_service: IStorageService = Depends(get_storage_service)): 
    file_prefix = (f"{client}_appointment_")
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
async def read_file(client: str,date_str: str,storage_service: IStorageService = Depends(get_storage_service)):
    file_name=(f"{client}_appointment_{date_str}.json")
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


##################################################################### 
@router.get("/{client}/status-report/{date_str}", status_code=status.HTTP_200_OK)
async def read_file(client: str, date_str: str,storage_service: IStorageService = Depends(get_storage_service)):
    file_name=(f"{client}_appointment_{date_str}.json")
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
    
@router.get("/{client}/individual-status/{phone_number}/days/{date_string}", status_code=status.HTTP_200_OK)
async def read_file(client: str, phone_number: str, date_string: str,storage_service: IStorageService  = Depends(get_storage_service)):
    
    try:
        ph_number = (f"+{phone_number}")
        number = ph_number.replace(' ', '')
        file_name=(f"{client}_appointment_{date_string}.json")
        filename = file_name.replace(' ', '')
        return await readfile_content_by_phone(filename,number,storage_service)
    except Exception as e:
        print(e)
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": "Internal Server Error"})
