import os

from app.services.common_service.db_service import DatabaseService


class RecentFile:
    async def find_recent_file(self, prefix):
        try:
            self.db_data = DatabaseService()
            file_name = await self.db_data.find_recent_documents(prefix)
            if file_name:
                return file_name
            else:
                return None
        except Exception as e:
            print(f"An error occurred while connecting to file storage : {e}")

        # folder_path = os.path.join(os.getcwd(), "temp")
        # # Get a list of all files in the folder that start with the specified prefix
        # files = [f for f in os.listdir(folder_path) if f.startswith(prefix) and os.path.isfile(os.path.join(folder_path, f))]
        
        # # If files are found, get the most recently modified file
        # if files:
        #     most_recent_file = max(files, key=lambda x: os.path.getmtime(os.path.join(folder_path, x)))
        #     return most_recent_file
        # else:
        #     return None