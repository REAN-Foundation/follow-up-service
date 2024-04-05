

from fastapi import APIRouter, HTTPException, Request
import boto3
from app.services.gghn_login_service import GghnUserLogin 
from app.services.gghn_patient_code_service import ExtractPatientCode

def readfile_content(date):
    try:
        print (date)
        login = GghnUserLogin()
        login.gghnlogin()
        patientextraction = ExtractPatientCode()
        appointmentcontent = patientextraction.read_content(date)
        return(appointmentcontent)
    except Exception as e:
         raise e