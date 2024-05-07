

from fastapi import APIRouter, HTTPException, Request
import boto3
from app.services.appointment.gghn_service.gghn_login_service import GghnUserLogin 
from app.services.appointment.gghn_service.gghn_patient_code_service import ExtractPatientCode
from app.services.appointment.gmu_service.login_service import UserLogin

def readfile_content(date):
    try:
        print (date)
        login = GghnUserLogin()
        login.gghnlogin()
        login = UserLogin()
        login.login()
        patientextraction = ExtractPatientCode()
        appointmentcontent = patientextraction.read_content(date)
        return(appointmentcontent)
        # return()
    except Exception as e:
         raise e