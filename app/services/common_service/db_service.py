from datetime import datetime
import os
import pymongo
from pymongo import MongoClient
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient

from app.interfaces.appointment_storage_interface import IStorageService 
load_dotenv()

class DatabaseService(IStorageService):
    def __init__(self):
        pass

    async def connect_storage(self,collect_prefix):
        connection_url = os.getenv("MONGODB_URL")
        ssl_cert = os.getenv("SSL_CERT_REQS")
        allow_invalid = os.getenv("ALLOW_INVALID_CERT")
        client = MongoClient(connection_url, ssl_cert_reqs = ssl_cert, tlsAllowInvalidCertificates = allow_invalid)
        # db = client['document_db']
        db = client.get_database(os.getenv("DATABASE_NAME"))
        if(collect_prefix == 'gghn'):
            record = db.get_collection(os.getenv("GGHN_COLLECTION_NAME"))
            return(record)
        if(collect_prefix == 'gmu'):
            record = db.get_collection(os.getenv("GMU_COLLECTION_NAME"))
            return(record)
    
    async def store_file(self,filename,content):
        prefix =  filename.split('_')
        collection_prefix = prefix[0]
        if(collection_prefix == 'temp'):
                collection_prefix = 'gmu'
        collection = await self.connect_storage(collection_prefix)
        time_stamp  = datetime.utcnow()
        document = {
                        "filename": filename,
                        "content": content,
                        "updatedAt": time_stamp
                    }
        # Insert the document into the collection
        collection.insert_one(document)
        print(f"Inserted {filename} into MongoDB")
        print("All json files have been pushed to MongoDB.")
        cnt = collection.count_documents({})
        print("count of records in collection",cnt)

    async def search_file(self, query):
        try:
            filename = query
            prefix =  filename.split('_')
            collection_prefix = prefix[0]
            if(collection_prefix == 'temp'):
                collection_prefix = 'gmu'
            # MongoDB Atlas connection string
            collection = await self.connect_storage(collection_prefix)
            # Define the query to filter documents
            query = {"filename": query}
            # Retrieve documents matching the query
            documents = collection.find_one(query)
            # Check if any documents were found
            if documents == None:
                print("No documents found matching the query.")
                return(None)
            else:
                # Process and print each document
                content = documents['content']
                # print(content)
                return(content)
        except pymongo.errors.ConnectionFailure as e:
            print(f"Could not connect to MongoDB: {e}")
        except pymongo.errors.PyMongoError as e:
            print(f"An error occurred: {e}")
    
    async def update_file(self, filename, update_content):
        file_name = filename
        prefix =  filename.split('_')
        collection_prefix = prefix[0]
        if(collection_prefix == 'temp'):
                collection_prefix = 'gmu'
        collection = await self.connect_storage(collection_prefix)
        filter = {"filename":file_name}
        resp = await self.search_file(file_name)
        if resp != None:
            print(type(update_content)) 
            update_fields = {
            'content': update_content,
            'updatedAt': datetime.utcnow()
            }
            update = {"$set": update_fields}
            print(type(update)) 
            # Update the document
            result = collection.update_one(filter, update)
            if result.matched_count > 0:
                print(f"Successfully updated {result.modified_count} document(s).")
                data = await self.search_file(file_name)
            else:
                print("No documents matched the filter.")
                data = None
        return(data)
    
    async def find_recent_documents(self, file_prefix):
        initial = file_prefix
        prefix =  initial.split('_')
        collection_prefix = prefix[0]
        print("initial",collection_prefix)
        collection = await self.connect_storage(collection_prefix)
        query = {'filename': {'$regex': f'^{file_prefix}'}}
        cursor = collection.find(query).sort('updatedAt', -1).limit(1)
        most_recent_file = next(cursor, None)
        if most_recent_file:
            return most_recent_file['filename']
        else:
             return None


       