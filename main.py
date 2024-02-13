from fastapi import FastAPI, APIRouter, Depends, HTTPException, status
from app.startup.application import app
from app.common.logger import logger
import os
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Run the application server
if __name__ == "__main__":
        PORT = int(os.getenv("PORT", 3232))
        logger.info("Running in production mode")
        uvicorn.run(app, host="0.0.0.0", port=3232)
