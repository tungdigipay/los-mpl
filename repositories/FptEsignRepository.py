from libraries import Hasura

def storage(applicationID, data):
    detail = detail_by_appID(applicationID)
    return __insert(applicationID, data)
    # if detail['status'] == True and detail['data'] != []:
    #     return __update(detail['data'][0]['ID'], data)
    # else:
    #     return __insert(applicationID, data)

def __update(ID, data):
    objects = create_objects(data)
    query = """
    mutation m_update_LOG_FPT_esigns_by_pk {
        update_LOG_FPT_esigns_by_pk(
            pk_columns: { ID: %d }, _set: { %s }
        ) {
            ID
        }
    }
    """ % (
        ID, objects
    )
    res = Hasura.process("m_update_LOG_FPT_esigns_by_pk", query)
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
    mutation m_insert_LOG_FPT_esigns_one {
        insert_LOG_FPT_esigns_one(
            object: {
                applicationID: %d, %s
            }
        ) {
            ID
        }
    }
    """ % ( applicationID, objects )
    res = Hasura.process("m_insert_LOG_FPT_esigns_one", query)
    if res['status'] == False:
        return res

    return {
        "status": True,
        "data": {
            "ID": res['data']['insert_LOG_FPT_esigns_one']['ID']
        }
    }

def create_objects(data) -> str:
    objects = ""
    if 'payload' in data:
        objects += 'payload: "%s", ' % (data['payload']).replace('"', '\\"')
    if 'response' in data:
        objects += 'response: "%s", ' % (data['response']).replace('"', '\\"')

    return objects

def detail_by_appID(applicationID):
    query = """
    query q_detail_by_appID {
        LOG_FPT_esigns(
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
        "data": res['data']['LOG_FPT_esigns']
    }