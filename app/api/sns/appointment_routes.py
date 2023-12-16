from fastapi import APIRouter, HTTPException, status
from fastapi import Request
from fastapi.responses import JSONResponse
from app.api.sns.appointment_handler import handle, readfile, readfile_content_by_phone, readfile_summary, update_reply_by_ph
from app.common.utils import get_temp_filepath

###############################################################################

router = APIRouter(
    prefix="/appointment-schedules/gmu",
    tags=["appointment-schedules", "gmu"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)

###############################################################################

@router.post("/upload")
async def handle_sns_notification(message: Request):
    try:
        print("Notification received")
        result = await handle(message)
        return JSONResponse(content=result)
    except Exception as e:
        print(e)
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": "Internal Server Error"})


@router.get("/appointment-status/{phone_number}/days/{date_string}", status_code=status.HTTP_200_OK)
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

@router.get("/status-report/{date_str}", status_code=status.HTTP_200_OK)
async def read_file(date_str: str):
    file_name=(f"gmu_followup_file{date_str}.json")
    filename = file_name.replace(' ', '')
    file_path = get_temp_filepath(filename)
    try:
        appointment_followup_data = await readfile(file_path)        
        followup_summary = await readfile_summary(file_path,filename)
        data = {
            "File_data":appointment_followup_data,
            "Summary":followup_summary 
            } 
        return(data)
    except Exception as e:
        print(e)
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": "Internal Server Error"})

@router.put("/appointment-status/{phone_number}/days/{date_str}",  status_code=status.HTTP_201_CREATED)
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


