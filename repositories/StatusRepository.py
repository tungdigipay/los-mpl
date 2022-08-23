from libraries import Hasura

def detail_application_by_unique(uniqueID):
    query = """
    query q_detail_application_by_unique {
        LOS_applications(
            where: { uniqueID: {_eq: "%s" } } , 
            limit: 1
        ) {
            ID
            LOS_customer {
                idNumber
                fullName
            }
            LOS_customer_profile {
                addressFull
                mobilePhone
                current_LOS_master_location_ward {
                    name
                }
                current_LOS_master_location_district {
                    name
                }
                current_LOS_master_location_province {
                    name
                }
            }
            loanAmount
            loanTenor
            contractNumber
            note
            LOS_status {
                ID
                alias
                description
                name
            }
        }
    }
    """ % (uniqueID)

    res = Hasura.process("q_detail_application_by_unique", query)
    if res['status'] == False:
        return []

    if res['data']['LOS_applications'] == []:
        return []

    return res['data']['LOS_applications'][0]

def detail_by_id(statusID):
    query = """
    query q_status_by_id {
        LOS_status_by_pk(ID: %d) {
            alias
            description
            ID
        }
    }
    """ % (statusID)

    res = Hasura.process("q_status_by_id", query)
    if res['status'] == False:
        return []

    if res['data']['LOS_status_by_pk'] == None:
        return []

    return res['data']['LOS_status_by_pk']