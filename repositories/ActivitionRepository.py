from libraries import Hasura

def detail_application(uniqueID):
    query = """
    query q_detail_application {
        LOS_applications(
            where: { uniqueID: {_eq: "%s"} }
        ) {
            ID
            uniqueID
            statusID
        }
    }
    """ % (uniqueID)
    res = Hasura.process("q_detail_application", query)
    if res['status'] == False:
        return []

    if res['data']['LOS_applications'] == []:
        return []

    return res['data']['LOS_applications'][0]