import os
import pymongo
from pymongo import MongoClient
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient 
load_dotenv()

class DatabaseService:
    def __init__(self):
        pass

    def connect_atlas(self,collect_prefix):
        connection_url = os.getenv("MONGODB_URL")
        client = MongoClient(connection_url)
        # db = client['document_db']
        db = client.get_database(os.getenv("DATABASE_NAME"))
        if(collect_prefix == 'gghn'):
            record = db.get_collection(os.getenv("GGHN_COLLECTION_NAME"))
            return(record)
        if(collect_prefix == 'gmu'):
            record = db.get_collection(os.getenv("GMU_COLLECTION_NAME"))
            return(record)
    
    def store_file(self,filename,content,collect_prefix):
        collection = self.connect_atlas(collect_prefix)
        document = {
                        "filename": filename,
                        "content": content
                    }
        # Insert the document into the collection
        collection.insert_one(document)
        print(f"Inserted {filename} into MongoDB")
        print("All json files have been pushed to MongoDB.")
        cnt = collection.count_documents({})
        print("count of records in collection",cnt)

    def search_file(self, query, collect_prefix):
        try:
            # MongoDB Atlas connection string
            collection = self.connect_atlas(collect_prefix)
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
                print(content)
                return(content)
        except pymongo.errors.ConnectionError as e:
            print(f"Could not connect to MongoDB: {e}")
        except pymongo.errors.PyMongoError as e:
            print(f"An error occurred: {e}")
    
    def update_file(self, filename, update_content, collect_prefix):
        file_name = filename
        collection = self.connect_atlas(collect_prefix)
        filter = {"filename":file_name}
        resp = self.search_file(file_name,collect_prefix)
        if resp != None:
            print(type(update_content)) 
            update = {"$set": {"content": update_content}}
            print(type(update)) 
            # Update the document
            result = collection.update_one(filter, update)
            if result.matched_count > 0:
                print(f"Successfully updated {result.modified_count} document(s).")
                data =  self.search_file(file_name,collect_prefix)
            else:
                print("No documents matched the filter.")
                data = None
        return(data)