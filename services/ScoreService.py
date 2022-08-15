import json
from libraries import Hasura
from services import ApplicationService
from helpers import CommonHelper

x1 = 0.75
x2 = 200000
x3 = 1.5
x4 = 1.5
x5 = 8
x6 = 25
x7 = 1.5

salary_region_1 = 4680000
salary_region_2 = 4160000
salary_region_3 = 3640000
salary_region_4 = 3250000

salary_hour_1 = 22500
salary_hour_2 = 20000
salary_hour_3 = 17500
salary_hour_4 = 15600
marks = ["A+", "A", "B+", "B", "C", "D"]

def process(uniqueID):
    application = detail_by_appID(uniqueID)
    if application['status'] == False:
        return application

    application = application['data']
    if application['statusID'] != 6:
        return {
            "status": False,
            "message": "Hồ sơ chưa đạt yêu cầu Score"
        }

    applicationID = application['ID']
    res_brc = business_rule_check(application)
    if res_brc['status'] == False:
        ApplicationService.update_status(application, 16, f"{res_brc['code']}_{res_brc['message']}")
        return res_brc

def detail_by_appID(uniqueID):
    query = """
    query detail_LOS_applications {
        LOS_applications(
            where: { 
                uniqueID: { _eq: "%s" } 
            }
        ) {
            LOS_customer {
                dateOfBirth
                LOS_master_gender{
                    score
                }
            }
            LOS_customer_profile {
                mobilePhone
                current_LOS_master_location_district {
                    salaryRegion
                }
                LOS_master_marital_status{
                    score
                }
            }
            LOS_master_employee_type {
                ID score
            }
            ID
            emi
            loanTenor
            statusID
            monthlyExpenses
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

def business_rule_check(application):
    emi = application['emi']
    ma = calc_ma(application) * 0.35
    if emi > ma:
        return {
            "status": False,
            "message": "Hồ sơ auto refusal hoặc CE cancel",
            "code": "SGN_canceled"
        }

    return {
        "status": True
    }

def de_matrix(application):
    dgp_rating = __dgp_rating(application)
    cs_grade = __cs_grade(application)

    dgp_index = marks.index(dgp_rating)
    cs_index = marks.index(cs_grade)

    matrix = __get_matrix()
    grade = matrix[dgp_index][cs_index]
    decision = __final_decision(grade)

    return {
        "status": True,
        "data": {
            "grade": grade,
            "decision": decision
        }
    }

def __final_decision(grade):
    decisions = {
        1: "Approve",
        2: "Approve",
        3: "Manual",
        4: "Cancel",
        5: "Cancel",
        6: "Cancel",
    }
    return decisions[grade]

def __get_matrix():
    return [
        [1, 1, 2, 2, 3, 5],
        [2, 2, 3, 3, 3, 5],
        [3, 3, 3, 3, 3, 5],
        [4, 4, 4, 4, 5, 5],
        [5, 5, 5, 5, 5, 6],
        [6, 6, 6, 6, 6, 6]
    ]

def __dgp_rating(application):
    birthday = application['LOS_customer']['dateOfBirth']
    age = __dgp_age(birthday)
    employment = application['LOS_master_employment_type']['score']
    marital = application['LOS_master_marital_status']['score']
    gender = application['LOS_customer']['LOS_master_gender']['score']
    product = __dgp_product(application)

    score = age + employment + marital + gender + product

    if score < 13.46:
        return "D"
    if score < 14.96:
        return "C"
    if score < 16.46:
        return "B"
    if score < 17.20:
        return "B+"
    if score < 17.95:
        return "A"
    return "A+"

def __cs_grade(application):
    cs = __credit_score(application)
    if cs <= 0.46:
        return "D", "Blackzone"
    if cs <= 0.57:
        return "C", "VH Risk"
    if cs <= 0.63:
        return "B", "High Risk"
    if cs <= 0.75:
        return "B+", "Med Risk"
    if cs <=  0.97:
        return "A", "Low Risk"
    if cs > 0.97:
        return "A+", "Low Risk"

    return "D", "Blackzone"

def calc_ma(application):
    income = calc_income(application)
    expense = calc_expense(application)
    return income - expense

def calc_expense(application, income):
    income = income * 0.6 - __loan_fi(application)
    return max(income, application['monthlyExpenses'])

def __loan_fi(application):
    ## current not connect to Loan FI
    return 0

def calc_income(application):
    employmentID = application['LOS_master_employment_type']['ID']
    income = application['monthlyIncome'] * x1
    salary_region, salary_hour = __salary_region(application)
    
    if employmentID in [1, 4]:
        salary_region = salary_region * x4
        ins_score = __ins_score(application) * x2 * x3
        return min(income, salary_region, ins_score)
    else:
        salara_by_hour = salary_hour * x5 * x6 * x7
        return min(income, salara_by_hour)

def __ins_score(application):
    record = json.loads('{"sInfos":[]}')
    data = record['sInfos']
    if data == []:
        return 0
    
    return data[0]['score']

def __salary_region(application):
    salaryRegion = application['LOS_customer_profile']['current_LOS_master_location_district']['salaryRegion']
    if salaryRegion == 1:
        return salary_region_1, salary_hour_1
    if salaryRegion == 2:
        return salary_region_2, salary_hour_2
    if salaryRegion == 3:
        return salary_region_3, salary_hour_3
    if salaryRegion == 4:
        return salary_region_4, salary_hour_4

def __dgp_age(birthday):
    age = CommonHelper.get_age(birthday)

    if age < 26:
        return 0
    if age < 31:
        return 1
    if age < 41:
        return 3
    if age < 51:
        return 2
    if age < 61:
        return 1
    
    return 0

def __dgp_product(application):
    ## hiện tại chỉ cho trả góp gotit
    return 2

def __credit_score(application):
    data = json.loads('{"score":0.6835727978021092,"version":"SCORING_SOCIAL_FRAUD_20220627"}')
    return data['score']