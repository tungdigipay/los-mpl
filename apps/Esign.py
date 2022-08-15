from libraries import EsignFPT

def preparing(agreementUUID):
    EsignFPT.prepareCertificateForSignCloud(agreementUUID)
    return EsignFPT.prepareFileForSignCloud(agreementUUID)

def authorize(agreementUUID, otpCode, BillCode):
    EsignFPT.authorizeCounterSigningForSignCloud(agreementUUID, otpCode, BillCode)