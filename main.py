import json
from fastapi import FastAPI, Request, HTTPException, status, File, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from apps import OTP, Files, Customers, Applications, Kyc
from models import OtpModel, OcrModel, FileModel, ApplicationModel, KycModel, GraphqlModel

from services import ApplicationService

app = FastAPI()

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({
            "status": False,
            "massage": exc.errors()[0]['msg'],
            "data": exc.errors()
        }),
    )

@app.get("/")
def root():
    return ApplicationService.mfast_blacklist("090111222", "0901112222")
    return "hello"

@app.post("/otp/request")
def request_otp(request: OtpModel.Item):
    return OTP.request(request)

@app.post("/otp/verify")
def verify_otp(request: OtpModel.Verify):
    return OTP.verify(request)

@app.post("/files/upload")
async def upload_file(request: FileModel.Item):
    file_result = await Files.upload(request.file)
    return {"filename": file_result}

@app.post("/ocr/storage")
async def ocr_storage(request: OcrModel.Item):
    return Applications.init(request)

@app.post("/kyc/storage")
async def ocr_storage(request: KycModel.Item):
    return Kyc.storage(request)

@app.post("/application/submit")
async def application_submit(request: ApplicationModel.Item):
    return Applications.submit(request)

@app.post("/actions")
async def m_actions(request: GraphqlModel.Item):
    return {
        "accessToken": "tùng"
    }