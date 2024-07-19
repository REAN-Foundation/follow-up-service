import asyncio
import schedule
import time
from datetime import datetime
# from fastapi import Depends
# from app.api.appointment.route import read_file
from app.api.appointment.handler import readfile_content

from app.dependency import get_storage_service

async def call_set_reminder_func():
    try:
        print("call_set_reminder_func is called")
        client = "gghn"
        # Get the current date in YYYY-MM-DD format
        current_date = datetime.now().strftime('%Y-%m-%d')
        # date_string = await format_date_(current_date)
        storage_service = get_storage_service() 
        response = await readfile_content(client, current_date, storage_service)
        # result = response.json()
        print("response generated",response)
        
    except Exception as e:
        print(f"Error: {e}")
        return(e)
    
def schedule_async_job():
    print("schedule_async_job is called")
    asyncio.run(call_set_reminder_func())
    return schedule.CancelJob

    # Schedule the API call (example: every day at 10:00 AM)
# schedule.every().day.at("10:00").do(call_api_with_date)

# schedule.every(1).minutes.do(schedule_async_job)
# print("Job scheduled")

def schedule_job(schedule_datetime: str):
    # Schedule the job at the specific datetime
    print(schedule_datetime)
    time_str = schedule_datetime.split(' ')
    schedule_time = time_str[1]
    # schedule_time = schedule_datetime.strftime("%H:%M")
    # schedule_date = schedule_datetime.strftime("%Y-%m-%d")

    schedule.every().day.at(schedule_time).do(schedule_async_job)
    print(f"Job scheduled for at {schedule_time}")


# Function to run the scheduler
def run_scheduler():
    print("Scheduler is running")
    while True:
        schedule.run_pending()
        time.sleep(1)

# Async function to start the scheduler
async def start_scheduler():
    print("start_scheduler is called")
    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, run_scheduler)
