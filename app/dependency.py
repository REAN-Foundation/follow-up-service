# dependencies.py
import os
from app.services.common_service.db_service import DatabaseService
from app.services.common_service.file_service import FileStorageService


def get_storage_service():
    storage_type = os.getenv("STORAGE_TYPE", "local")
    if storage_type == "db":
       return DatabaseService()
    return FileStorageService()
# containers.py
# from app.services.common_service.db_service import DatabaseService
# from app.services.common_service.file_service import FileStorageService
# from dependency_injector import containers, providers
# import os

# class Container(containers.DeclarativeContainer):
#     config = providers.Configuration()
    
#     storage_service = providers.Selector(
#         config.storage_type,
#         local=providers.Factory(FileStorageService),
#         mongo=providers.Factory(DatabaseService),
#     )
