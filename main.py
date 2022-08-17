import json
from fastapi import FastAPI, Request, HTTPException, status, File, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from apps import OTP, Files, Customers, Applications, Kyc, Hyperverge, Prescore, Esign, Score
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

@app.post("/applications/prescore")
async def applications_prescore(request: ApplicationModel.Prescore):
    return Prescore.process(request.uniqueID)

@app.post("/applications/score")
async def applications_prescore(request: ApplicationModel.Score):
    return Score.process(request.uniqueID)

@app.post("/actions")
async def m_actions(request: GraphqlModel.Item):
    return {
        "accessToken": "tùng"
    }

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

@app.get("/sms")
def sms():
    from services import SmsSevice
    return SmsSevice.reject('0905044591')

@app.post("/esign/verify")
def esign_verify(request: EsignModel.Verify):
    return Esign.verify(request)

@app.post("/esign/otp")
def esign_otp(request: EsignModel.Otp):
    # return Esign.request_otp(request)
    return {
        "uniqueID": "3f7836d6-2651-4a4a-8159-cb78c42c4ea2"
    }

@app.post("/esign/confirm")
def esign_confirm(request: EsignModel.Confirm):
    # from services import EsignService
    # return EsignService.process(request)
    return {
        "status": True,
        "message": "Thành công"
    }


@app.get("/matrix/{dgp_rating}/{cs_grade}")
def matrix(dgp_rating, cs_grade):
    from services import ScoreService
    marks = ["A+", "A", "B+", "B", "C", "D"]
    dgp_index = marks.index(dgp_rating)
    cs_index = marks.index(cs_grade)
    matrix = [
        [1, 1, 2, 2, 3, 5],
        [2, 2, 3, 3, 3, 5],
        [3, 3, 3, 3, 3, 5],
        [4, 4, 4, 4, 5, 5],
        [5, 5, 5, 5, 5, 6],
        [6, 6, 6, 6, 6, 6]
    ]

    grade = matrix[dgp_index][cs_index]
    decisions = {
        1: "Approve",
        2: "Approve",
        3: "Manual",
        4: "Cancel",
        5: "Cancel",
        6: "Cancel",
    }
    return decisions[grade]

@app.get("/cs")
def social_insurance():
    from datetime import date
    today = date.today()
    contract_number = "11" + today.strftime("%y%m%d")

    applicationID = 123456789
    applicationID_text = str(applicationID)
    if applicationID > 10000: applicationID_text = applicationID_text[-4:len(applicationID_text)]
    else: applicationID_text = applicationID_text.zfill(4)
    return applicationID_text
    

    return contract_number + applicationID_text
    # from repositories import ScoringReposirity
    # return ScoringReposirity.storage({
    #     "ID": 124
    # }, {
    #     "dgp_rating": "A"
    # })
    # return ApplicationService.social_insurance("090111222")

@app.get("/pdf")
async def pdf():
    from libraries import S3
    file_uploaded = S3.upload("files/esign/contract_template.pdf", "contract_template.pdf")
    return file_uploaded
    # from libraries import CreatePDF
    # return CreatePDF.gen()