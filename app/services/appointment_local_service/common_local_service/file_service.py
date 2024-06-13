import json
import os
from app.interfaces.appointment_storage_interface import DatabaseStorageI


class FileStorageService(DatabaseStorageI):
    def __init__(self):
        pass

    async def connect_storage(self,filename):
        try:
            temp_folder = os.path.join(os.getcwd(), "temp")
            f_path=(os.getcwd()+"/temp/"+filename)
            if os.path.exists(f_path):
                print(f"The file {filename} already exists!")
                return f_path
            if not os.path.exists(temp_folder):
                os.mkdir(temp_folder)
                f_path = os.path.join(temp_folder, filename)
                return f_path
            else:
                f_path = os.path.join(temp_folder, filename)
                return f_path
        except Exception as e:
            print(f"An error occurred while connecting to file storage : {e}")
    
    async def store_file(self, filename, content):
        try:
            if filename.startswith("gghn_details"):
                indent_given = 25
            if filename.startswith("gghn_appointment"):
                indent_given = 6  
            indent_given = 7      
            f_path = await self.connect_storage(filename)
            with open(f_path, 'w') as json_file:
                json.dump(content, json_file, indent = indent_given )
            return(filename)
        except Exception as e:
            print(f"An error occurred while storing in file: {e}")

    async def search_file(self,filename):
        try:
            f_path=(os.getcwd()+"/temp/"+filename)
            if not os.path.exists(f_path):
                return None
            else:
                file=open(f_path,"r")
                file_content=file.read()
                data=json.loads(file_content)
                return data
        except Exception as e:
            print(f"An error occurred while searching file: {e}")
    
    async def update_file(self, filename, content):
        try:
            if filename.startswith("gghn_details"):
                indent_given = 25
            if filename.startswith("gghn_appointment"):
                indent_given = 6  
            indent_given = 7 
            f_path = await self.connect_storage(filename)
            with open(f_path, 'w') as json_file:
                json.dump(content, json_file,indent = indent_given)
            return(filename)
        except Exception as e:
            print(f"An error occurred while updating in file: {e}")
    
    async def find_recent_documents(self, prefix):
        folder_path = os.path.join(os.getcwd(), "temp")
        # Get a list of all files in the folder that start with the specified prefix
        files = [f for f in os.listdir(folder_path) if f.startswith(prefix) and os.path.isfile(os.path.join(folder_path, f))]
        
        # If files are found, get the most recently modified file
        if files:
            most_recent_file = max(files, key=lambda x: os.path.getmtime(os.path.join(folder_path, x)))
            return most_recent_file
        else:
            return None


       