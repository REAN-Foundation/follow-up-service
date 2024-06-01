import os
class RecentFile:

    async def find_recent_file(self, prefix):
        folder_path = os.path.join(os.getcwd(), "temp")
        # Get a list of all files in the folder that start with the specified prefix
        files = [f for f in os.listdir(folder_path) if f.startswith(prefix) and os.path.isfile(os.path.join(folder_path, f))]
        
        # If files are found, get the most recently modified file
        if files:
            most_recent_file = max(files, key=lambda x: os.path.getmtime(os.path.join(folder_path, x)))
            return most_recent_file
        else:
            return None