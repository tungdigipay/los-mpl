from libraries import Hasura

def record(input, payload, resultContent):
    objects = __create_objects(input)
    query = """
    mutation m_insert_LOS_scoring_logs($data: jsonb = "", $resultContent: jsonb = "") {
        insert_LOS_scoring_logs(
            objects: {
                data: $data, 
                resultContent: $resultContent, 
                %s
            }
        ) {
            returning {
                ID
            }
        }
    }

    """ % (objects)
    variables = {
        "resultContent": resultContent,
        "data": payload
    }
    res = Hasura.process("m_insert_LOS_scoring_logs", query, variables)
    return res
    
def __create_objects(data) -> str:
    objects = ""
    if 'applicationID' in data:
        objects += 'applicationID: %d, ' % (data['applicationID'])
    if 'result' in data:
        objects += 'result: "%s", ' % (data['result'])
    if 'type' in data:
        objects += 'type: "%s", ' % (data['type'])
    if 'logServiceID' in data:
        objects += 'logServiceID: %d, ' % (data['logServiceID'])
    if 'label' in data:
        objects += 'label: "%s", ' % (data['label'])

    return objects