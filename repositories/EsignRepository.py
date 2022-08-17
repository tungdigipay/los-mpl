from libraries import Hasura

def storage(application, data):
    applicationID = application['ID']
    detail = detail_by_appID(applicationID)
    if detail['status'] == True and detail['data'] != []:
        return __update(detail['data'][0]['ID'], data)
    else:
        return __insert(applicationID, data)

def __update(ID, data):
    objects = create_objects(data)
    query = """
    mutation m_update_LOS_application_esigns_by_pk {
        update_LOS_application_esigns_by_pk(
            pk_columns: { ID: %d }, _set: { %s }
        ) {
            ID
        }
    }
    """ % (
        ID, objects
    )
    res = Hasura.process("m_update_LOS_application_esigns_by_pk", query)
    if res['status'] == False:
        return res

    return {
        "status": True,
        "data": {
            "ID": ID
        }
    }

def __insert(applicationID, data):
    objects = create_objects(data)
    query = """
    mutation m_insert_LOS_application_esigns_one {
        insert_LOS_application_esigns_one(
            object: {
                applicationID: %d, %s
            }
        ) {
            ID
        }
    }
    """ % ( applicationID, objects )
    res = Hasura.process("m_insert_LOS_application_esigns_one", query)
    if res['status'] == False:
        return res
    return {
        "status": True,
        "data": {
            "ID": res['data']['insert_LOS_application_esigns_one']['ID']
        }
    }

def create_objects(data) -> str:
    objects = ""
    if 'esignPwd' in data:
        objects += 'esignPwd: "%s", ' % (data['esignPwd'])
    if 'contractFile' in data:
        objects += 'contractFile: "%s", ' % (data['contractFile'])

    return objects

def detail_by_appID(applicationID):
    query = """
    query q_detail_by_appID {
        LOS_application_esigns(
            where: {
                applicationID: { _eq: %d }, 
            }
        ) {
            applicationID ID
        }
    }
    """ % (applicationID)
    res = Hasura.process("q_detail_by_appID", query)
    if res['status'] == False:
        return res

    return {
        "status": True,
        "data": res['data']['LOS_application_esigns']
    }

def verify_application(contractNumber, idNumber, esignPwd):
    query = """
    query q_LOS_application_esigns {
        LOS_application_esigns(
            where: {
                LOS_application: {
                    statusID: { _eq: 14 },
                    contractNumber: {_eq: "%s"}, 
                    LOS_customer: {idNumber: {_eq: "%s"} } 
                }, 
                esignPwd: {_eq: "%s"}
            }
        ) {
            contractFile
            LOS_application {
                ID
                uniqueID
                LOS_customer_ocrs {
                    idNumberFrontImage
                }
                LOS_customer_profile {
                    mobilePhone
                }
            }
        }
    }
    """ % (contractNumber, idNumber, esignPwd)
    res = Hasura.process("q_LOS_application_esigns", query)
    if res['status'] == False:
        return res

    return {
        "status": True,
        "data": res['data']['LOS_application_esigns']
    }

def detail_for_esign(uniqueID):
    query = """
    query q_detail_for_esign {
        LOS_applications(
            where: { uniqueID: {_eq: "%s"} }
        ) {
            ID
        }
    }
    """ % (uniqueID)
    res = Hasura.process("q_detail_for_esign", query)
    if res['status'] == False:
        return res

    return {
        "status": True,
        "data": res['data']['LOS_application_esigns']
    }