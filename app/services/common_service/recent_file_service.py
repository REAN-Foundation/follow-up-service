import os

from fastapi import HTTPException

from app.services.common_service.db_service import DatabaseService


class RecentFile:
    async def find_recent_file(self, file_prefix):
        try:
            self.db_connect = DatabaseService()
            most_recent_file = await self.db_connect.find_recent_documents(file_prefix)
            file_name =  most_recent_file['filename']
            return file_name
        except Exception as e:
            raise HTTPException(status_code=404, detail=str(e))