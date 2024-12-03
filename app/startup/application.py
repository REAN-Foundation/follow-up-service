import asyncio
from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.common.exceptions import add_exception_handlers
from app.startup.router import router
import logging

#################################################################
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Lifespan started")
    # Startup code
    # asyncio.create_task(start_scheduler())
    yield
    # Shutdown code (if needed)

def get_application():

    server = FastAPI(lifespan=lifespan)

    # Add CORS middleware
    server.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )
    server.include_router(router)

    return server

app = get_application()
add_exception_handlers(app)
