import json
from uuid import UUID
from fastapi import FastAPI, Request, HTTPException, status, File, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from apps import OTP, Files, Customers, Applications, Kyc, Hyperverge, Prescore, Esign, Score, Postback, Delivery
from models import OtpModel, OcrModel, FileModel, ApplicationModel, KycModel, GraphqlModel, EsignModel

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
            "message": exc.errors()[0]['msg'],
            "data": exc.errors()
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

@app.get("/applications/prescore")
async def applications_prescore(uniqueID: UUID):
    return Prescore.process(uniqueID)

@app.get("/applications/score")
async def applications_prescore(uniqueID: UUID):
    return Score.process(uniqueID)

@app.post("/hyperverge/login")
async def login():
    return Hyperverge.login()

@app.post("/esign/preparing")
def esign_preparing(request: EsignModel.Preparing):
    return Esign.preparing(request.agreementUUID)

@app.post("/esign/authorize")
def esign_authorize(request: EsignModel.Authorize):
    return Esign.authorize(request.agreementUUID, request.otpCode, request.billCode)

@app.get("/kalapa/{item}")
def kalapa(item):
    from libraries import Kalapa
    if item == "check_mobilephone":
        return ApplicationService.check_mobilephone("0905044591")
    if item == "social_insurance":
        return ApplicationService.social_insurance("205341091")

@app.post("/esign/verify")
def esign_verify(request: EsignModel.Verify):
    return Esign.verify(request)

@app.post("/esign/otp")
def esign_otp(request: EsignModel.Otp):
    return Esign.request_otp(request)

@app.post("/esign/confirm")
def esign_confirm(request: EsignModel.Confirm):
    return Esign.confirm(request)

@app.post("/esign/email")
def esign_email(request: EsignModel.Email):
    return Esign.email(request.uniqueID, request.email)

@app.get("/postback/status")
async def postback_status(uniqueID: UUID):
    return Postback.status(uniqueID)

@app.get("/delivery/{action}")
async def delivery_order(action: str, uniqueID: UUID):
    if action == "order":
        return Delivery.order(uniqueID)
    if action == "packing":
        return Delivery.packing(uniqueID)
    if action == "shipping":
        return Delivery.shipping(uniqueID)
    if action == "delivered":
        return Delivery.delivered(uniqueID)
    
    return {
        "detail": "No action"
    }

@app.get("/pdf")
async def pdf():
    # from helpers import CommonHelper
    # return CommonHelper.number_to_text(1160000)
    from services import EsignService
    application = {"ID": 2}
    res = EsignService.__update_application(application, {
        "statusID": 14,
        "note": "Đã sinh hợp đồng và chờ khách hàng ký",
        "contractNumber": "112208250002"
    })
    application = res['data']['update_LOS_applications_by_pk']

    contractFile = EsignService.__contract_file(application, "112208250002")
    return contractFile