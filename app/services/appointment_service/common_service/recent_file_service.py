import os

from fastapi import HTTPException

from app.services.appointment_service.common_service.db_service import DatabaseService
class RecentFile:
    def find_recent_file(file_prefix):
        try:
            prefix = file_prefix.split('_')
            collection_prefix = prefix[0]
            db_connect = DatabaseService()
            most_recent_file = db_connect.find_recent_documents(file_prefix, collection_prefix)
            file_name =  most_recent_file['filename']
            return file_name
        except Exception as e:
            raise HTTPException(status_code=404, detail=str(e))