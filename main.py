from fastapi import FastAPI, Request, HTTPException, status, File, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from apps import OTP, Files, Customers
from models import OtpModel, OcrModel

app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://appay.cloudcms.test"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
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
            "massage": exc.errors()[0]['msg']
        }),
    )

@app.get("/")
def root():
    return "hello"

@app.post("/otp/request")
def request_otp(request: OtpModel.Item):
    return OTP.request(request)

@app.post("/otp/verify")
def verify_otp(request: OtpModel.Verify):
    return OTP.verify(request)

@app.post("/files/upload")
async def upload_file(file: UploadFile):
    file_result = await Files.upload(file)
    return {"filename": file_result}

@app.post("/ocr/storage")
async def ocr_storage(request: OcrModel.Item):
    return Customers.storage(request)