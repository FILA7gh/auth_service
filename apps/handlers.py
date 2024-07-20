from fastapi import status, Request
from fastapi.encoders import jsonable_encoder
from pydantic import ValidationError
from starlette.responses import JSONResponse

from main import app


@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({'detail': exc.errors()})
    )
