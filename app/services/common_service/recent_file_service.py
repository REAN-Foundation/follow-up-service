import os

from fastapi import HTTPException

from app.services.common_service.db_service import DatabaseService


class RecentFile:
    async def find_recent_file(self, file_prefix,storage_service):
        try:
            # self.db_connect = DatabaseService()
            file_name = await storage_service.find_recent_documents(file_prefix)
            return file_name
        except Exception as e:
            raise HTTPException(status_code=404, detail=str(e))