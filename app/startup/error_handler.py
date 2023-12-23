from fastapi import Request, status
from app.common.logger import logger
from app.startup.application import app
from app.common.exceptions import HTTPError
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
# from sqlalchemy.exc import SQLAlchemyError
import traceback2 as traceback

#################################################################

# Predefined Commonly raised HTTP Errors+-*/

@app.exception_handler(HTTPError)
async def api_error_handler(request: Request, exc: HTTPError):

    # Handle telemetry and logging here...
    logger.error(f"API Error: {exc.message}")
    traceback.print_exception(type(exc), exc, exc.__traceback__)

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "Message": exc.message,
            "Status": "Failure",
            "Data" : None
        },
    )

# Validation Errors

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):

    # Handle telemetry and logging here...
    logger.error(f"Validation Error: {exc.errors()}")
    traceback.print_exception(type(exc), exc, exc.__traceback__)

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder(
            {
                "Message": "Validation Error",
                "Status": "Failure",
                "Errors": exc.errors(),
                                "RequestBody": exc.body
            }
        ),
    )

# Generic Errors

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    # Handle telemetry and logging here...
    logger.error(f"Internal Server Error: {exc.args}")
    traceback.print_exception(type(exc), exc, exc.__traceback__)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=jsonable_encoder(
            {
                "Message": "Internal Server Error",
                "Status": "Failure",
                "Errors": exc.args,
            }
        ),
    )
