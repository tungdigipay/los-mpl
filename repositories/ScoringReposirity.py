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
    mutation m_update_LOS_application_scoring_by_pk {
        update_LOS_application_scoring_by_pk(
            pk_columns: { ID: %d }, _set: { %s }
        ) {
            ID
        }
    }
    """ % (
        ID, objects
    )
    res = Hasura.process("m_update_LOS_application_scoring_by_pk", query)
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
    mutation m_insert_LOS_application_scoring_one {
        insert_LOS_application_scoring_one(
            object: {
                applicationID: %d, %s
            }
        ) {
            ID
        }
    }
    """ % ( applicationID, objects )
    res = Hasura.process("m_insert_LOS_application_scoring_one", query)
    if res['status'] == False:
        return res
    return {
        "status": True,
        "data": {
            "ID": res['data']['insert_LOS_application_scoring_one']['ID']
        }
    }

def create_objects(data) -> str:
    objects = ""
    if 'ma' in data:
        objects += "ma: %d, " % (data['ma'])
    if 'dgp_rating' in data:
        objects += 'dgp_rating: "%s", ' % (data['dgp_rating'])
    if 'credit_score' in data:
        objects += 'credit_score: %d, ' % (data['credit_score'])
    if 'cs_grade' in data:
        objects += 'cs_grade: "%s", ' % (data['cs_grade'])
    if 'social_score' in data:
        objects += 'social_score: %d, ' % (data['social_score'])
    if 'social_insurance' in data:
        objects += 'social_insurance: "%s", ' % (data['social_insurance'])
    if 'decision_mark' in data:
        objects += 'decision_mark: %d, ' % (data['decision_mark'])

    return objects

def detail_by_appID(applicationID):
    query = """
    query q_LOS_application_scoring {
        LOS_application_scoring(
            where: { 
                applicationID: { _eq: %d } 
            }
        ) {
            ID
            applicationID
            ma
            dgp_rating
            credit_score
            cs_grade
            social_score
            social_insurance
            decision_mark
        }
    }
    """ % (applicationID)
    res = Hasura.process("q_LOS_application_scoring", query)
    if res['status'] == False:
        return res

    return {
        "status": True,
        "data": res['data']['LOS_application_scoring']
    }