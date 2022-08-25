from libraries import Hasura
from helpers import CommonHelper

def detail_by_appID(uniqueID):
    query = """
    query detail_LOS_applications {
        LOS_applications(
            where: { 
                uniqueID: { _eq: "%s" } 
            }
        ) {
            ID
            LOS_customer {
                dateOfBirth
            }
            monthlyIncome
            reference1Name
            reference1Phone
            reference1Relationship
            reference2Name
            reference2Phone
            reference2Relationship
            LOS_customer_profile {
                currentAddressProvince
                mobilePhone
                current_LOS_master_location_district {
                    allow
                }
            }
            loanTenor
            statusID
        }
    }
    """ % (uniqueID)
    res = Hasura.process("detail_LOS_applications", query)
    if res['status'] == False:
        return res
    
    return {
        "status": True,
        "data": res['data']['LOS_applications'][0]
    }

def count_loan_by_phone(mobilePhone):
    query = """
    query count_loan_by_phone {
        LOS_applications_aggregate(
            where: {
                LOS_customer_profile: {mobilePhone: {_eq: "%s"} }, 
                statusID: { _eq: 23 } 
            }
        ) {
            aggregate {
                count
            }
        }
    }
    """ % (mobilePhone)
    res = Hasura.process("count_loan_by_phone", query)
    if res['status'] == False:
        return 0
    
    return res['data']['LOS_applications_aggregate']['aggregate']['count']

def count_processing_by_phone(mobilePhone):
    processing_status_ids = CommonHelper.list_status_for_processing()
    status_ids = [str(element) for element in processing_status_ids]
    query = """
    query count_loan_by_phone {
        LOS_applications_aggregate(
            where: {
                LOS_customer_profile: {mobilePhone: {_eq: "%s"} }, 
                statusID: { _in: [%s] } 
            }
        ) {
            aggregate {
                count
            }
        }
    }
    """ % (mobilePhone, ', '.join(status_ids))
    res = Hasura.process("count_loan_by_phone", query)
    if res['status'] == False:
        return 0
    
    return res['data']['LOS_applications_aggregate']['aggregate']['count']

def count_refused_by_phone(mobilePhone):
    thirty_days_ago = CommonHelper.thirty_days_ago()

    processing_status_ids = CommonHelper.list_status_for_refused()
    status_ids = [str(element) for element in processing_status_ids]

    query = """
    query count_loan_by_phone {
        LOS_applications_aggregate(
            where: {
                LOS_customer_profile: {mobilePhone: {_eq: "%s"} }, 
                statusID: { _in: [%s] }, 
                createdDate: { _gt: "%s"}
            }
        ) {
            aggregate {
                count
            }
        }
    }
    """ % (mobilePhone, ', '.join(status_ids), thirty_days_ago)
    res = Hasura.process("count_loan_by_phone", query)
    if res['status'] == False:
        return 0
    
    return res['data']['LOS_applications_aggregate']['aggregate']['count']