from abc import ABC, abstractmethod


class DatabaseStorageI(ABC):
    @abstractmethod
    async def connect_storage():pass

    @abstractmethod
    async def store_file():pass
       
    @abstractmethod
    async def search_file():pass
       
    @abstractmethod  
    async def update_file():pass

    @abstractmethod       
    async def find_recent_documents():pass
     