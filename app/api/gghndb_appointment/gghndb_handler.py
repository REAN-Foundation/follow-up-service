

from fastapi import APIRouter, HTTPException, Request
import boto3
from app.services.gghn_login_service import GghnUserLogin 
from app.services.gghn_patient_code_service import ExtractPatientCode
from app.services.login_service import UserLogin

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