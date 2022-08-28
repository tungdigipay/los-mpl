from libraries import Hasura

def record(input):
    objects = __create_objects(input)
    payload = input['payload']
    resultContent = input['resultContent']
    variables = {
        "resultContent": resultContent,
        "data": payload,
        "responseData": input['responseData']
    }

    detail = detail_by_applicationID(input['applicationID'], input['type'])
    if detail == []:
        return __insert(objects, variables)
    return __update(detail['ID'], objects, variables)
    
    
def __create_objects(data) -> str:
    objects = ""
    if 'applicationID' in data:
        objects += 'applicationID: %d, ' % (data['applicationID'])
    if 'result' in data:
        objects += 'result: "%s", ' % (data['result'])
    if 'type' in data:
        objects += 'type: "%s", ' % (data['type'])
    if 'logServiceID' in data and data['logServiceID'] != None:
        objects += 'logServiceID: %d, ' % (data['logServiceID'])
    if 'label' in data:
        objects += 'label: "%s", ' % (data['label'])

    return objects

def detail_by_applicationID(applicationID, type):
    query = """
    query detail_scoring {
        LOS_scoring_logs(
            where: {
                applicationID: { _eq: %d },
                type: { _eq: %s },
            }
        ) {
            ID
        }
    }
    """ % (applicationID, type)
    res = Hasura.process("detail_scoring", query)

    if res['status'] == False:
        return []

    if res['data']['LOS_scoring_logs'] == []:
        return []

    return res['data']['LOS_scoring_logs'][0]

def __insert(objects, variables):
    query = """
    mutation m_insert_LOS_scoring_logs($data: jsonb = "", $resultContent: jsonb = "", $responseData: jsonb = "") {
        insert_LOS_scoring_logs(
            objects: {
                data: $data, 
                resultContent: $resultContent, 
                responseData: $responseData
                %s
            }
        ) {
            returning {
                ID
            }
        }
    }
    """ % (objects)
    res = Hasura.process("m_insert_LOS_scoring_logs", query, variables)
    return res

def __update(ID, objects, variables):
    query = """
    mutation m_update_LOS_scoring_logs($data: jsonb = "", $resultContent: jsonb = "", $responseData: jsonb = "") {
        update_LOS_scoring_logs_by_pk(
            pk_columns: { ID: %d }, 
            _set: {
                data: $data, 
                resultContent: $resultContent, 
                responseData: $responseData
                %s
            }
        ) {
            ID
        }
    }
    """ % (ID, objects)
    res = Hasura.process("m_update_LOS_scoring_logs", query, variables)
    return res