from fastapi import FastAPI, Request, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from apps import OTP
from models import OtpModel

app = FastAPI()

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({
            "status": False,
            "massage": exc.errors()[0]['msg']
        }),
    )

@app.get("/")
def hello():
    return "Hello"

@app.post("/otp/request")
def request_otp(request: OtpModel.Item):
    return OTP.request(request)

@app.post("/otp/verify")
def verify_otp(request: OtpModel.Verify):
    return OTP.verify(request)