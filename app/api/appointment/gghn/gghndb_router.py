import os
from fastapi import APIRouter, HTTPException, status
from fastapi import Request
from fastapi.responses import JSONResponse
from app.common.appointment.appointment_utils import find_recent_file_from_atlas
from app.common.base_response import BaseResponseModel
from app.common.cache import cache
from app.api.appointment.gghn.gghndb_handler import read_appointment_file, readfile_content, readfile_summary, recent_file, update_gghn_reply_by_ph
from app.common.response_model import ResponseModel
from app.common.utils import find_recent_file_with_prefix, get_temp_filepath
##################################################################################
router = APIRouter(
    prefix="/appointment-schedules/gghn",
    tags=["appointment-schedules", "gghn"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)
#################################################################################
@router.get("/set-reminders/date/{date_string}", status_code=status.HTTP_201_CREATED,response_model=ResponseModel[BaseResponseModel|None])
async def read_file(date_string: str):
    try:
        response = await readfile_content(date_string)
        return {
            "Message" : "Reminders created successfully",
            "Data" : response
        } 
    except Exception as e:
        print(e)
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": "Internal Server Error"})

 # Here i have changed the route from appointment-status to appointment-reply       
@router.put("/appointment-reply/{phone_number}/day/{date_str}",  status_code=status.HTTP_201_CREATED)
async def update_reply_and_whatsappid_by_ph(phone_number: str, new_data: dict, date_str: str):
    try:
        print(phone_number)
        ph_number = (f"+{phone_number}")
        number = ph_number.replace(' ', '')
        file_name=(f"gghn_appointment_{date_str}.json")
        filename = file_name.replace(' ', '')
     
        content = new_data
        updated_data = await update_gghn_reply_by_ph(filename, number, content)
        return {
            "Message" : "Updated response successfully",
            "Data" : updated_data
        } 
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    
@router.get("/recent-status-report/recent-file", status_code=status.HTTP_200_OK)
async def read_file():
    file_prefix = "gghn_appointment_"
    filename = await recent_file(file_prefix)
    print(filename)

    try:
        gghn_appointment_followup_data = await read_appointment_file(filename)        
        followup_summary = await readfile_summary(filename)
        data = {
            "Summary":followup_summary,
            "File_data":gghn_appointment_followup_data,
            } 
        return(data)
    except Exception as e:
        print(e)
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": "Recent file error"})

@router.get("/status-report/{date_str}", status_code=status.HTTP_200_OK)
async def read_file(date_str: str):
    file_name=(f"gghn_appointment_{date_str}.json")
    filename = file_name.replace(' ', '')
   
    try:
        appointment_followup_data = await read_appointment_file(filename)        
        followup_summary = await readfile_summary(filename)
        data = {
            "Summary":followup_summary,
            "File_data":appointment_followup_data
            } 
        return(data)
    except Exception as e:
        print(e)
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": "Internal Server Error"})