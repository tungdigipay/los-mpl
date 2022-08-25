import json
from libraries import Hasura
from services import ApplicationService, EsignService
from helpers import CommonHelper
from repositories import ScoringReposirity

X0 = 20000000
X1 = 0.75
X2 = 200000
X3 = 1.5
X4 = 1.5
X5 = 8
X6 = 25
X7 = 1.5
X8 = 15000000


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
        ScoringReposirity.storage(application, {
            "ma": res_brc['data']['ma'],
        })
        ApplicationService.update_status(application, 12, f"{res_brc['code']}_{res_brc['message']}")
        return res_brc

    ma = res_brc['data']['ma']
    logic_de = de_matrix(application, ma)

    if logic_de['status'] == False:
        return logic_de

    if logic_de['data']['decision'] == "Approve":
        statusID = 10
        note = "Hồ sơ auto approval hoặc CE approve"
    elif logic_de['data']['decision'] == "Manual":
        statusID = 13
        note = "Kết quả DE vào nhóm Precise assessment và đang chờ CE xử lý"
    else:
        statusID = 12
        note = "DGP cus rate %s and CS grade %s" % (logic_de['data']['dgp_rating'], logic_de['data']['cs_grade'])
    
    ApplicationService.update_status(application, statusID, note)

    score_repo = {
        "ma": ma,
        "dgp_rating": logic_de['data']['dgp_rating'],
        "cs_grade": logic_de['data']['cs_grade'],
        "decision_mark": logic_de['data']['grade'],
    }
    ScoringReposirity.storage(application, score_repo)

    if statusID == 10:
        return EsignService.preparing(application)
    return {
        "status": True,
        "message": note
    }

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
                idNumber
                LOS_master_gender{
                    score
                }
            }
            LOS_customer_profile {
                mobilePhone
                current_LOS_master_location_district {
                    salaryRegion
                    minimumExpenseRegion
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
            monthlyIncome
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
    ma = calc_ma(application) * 0.8
    if emi > ma:
        return {
            "status": False,
            "message": "EMI cao hơn mức sống theo quy định ",
            "code": "EMI_EMAR",
            "data": {
                "ma": ma
            }
        }

    return {
        "status": True,
        "data": {
            "ma": ma
        }
    }

def de_matrix(application, ma):
    dgp_rating = __dgp_rating(application, ma)
    cs_grade, cs_group = __cs_grade(application)

    dgp_index = marks.index(dgp_rating)
    cs_index = marks.index(cs_grade)

    matrix = __get_matrix()
    grade = matrix[dgp_index][cs_index]
    decision = __final_decision(grade)

    return {
        "status": True,
        "data": {
            "grade": grade,
            "decision": decision,
            "dgp_rating": dgp_rating,
            "cs_grade": cs_grade
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

def __dgp_rating(application, ma):
    birthday = application['LOS_customer']['dateOfBirth']
    age = calc_density("age", __dgp_age(birthday))
    employment = calc_density("employment", application['LOS_master_employee_type']['score'])
    marital = calc_density("marital", application['LOS_customer_profile']['LOS_master_marital_status']['score'])
    gender = calc_density("gender", application['LOS_customer']['LOS_master_gender']['score'])
    product = calc_density("product", __dgp_product(application))
    ma_score = calc_density("ma", __ma_score(ma))
    agent = calc_density("agent", 1.5)
    group_customer = calc_density("group_customer", 2.5)

    score = age + employment + marital + gender + product + ma_score

    if score >= 2.65:
        return "A+"
    if score >= 2.54:
        return "A"
    if score >= 2.43:
        return "B+"
    if score >= 2.21:
        return "B"
    if score >= 1.99:
        return "C"
    return "D"

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

def calc_expense(application):
    minimum_expense = application['LOS_customer_profile']['current_LOS_master_location_district']['minimumExpenseRegion']
    minimum_expense = 0 if minimum_expense == None else minimum_expense
    max_expense = max(application['monthlyExpenses'], minimum_expense)
    obligation = __loan_fi(application) + minimum_expense
    return max(max_expense, obligation)

def __loan_fi(application):
    ## current not connect to Loan FI
    return 0

def calc_income(application):
    employmentID = application['LOS_master_employee_type']['ID']
    income = application['monthlyIncome']
    salary_region, salary_hour = __salary_region(application)
    
    if employmentID in [1, 4]:
        ins_score = __ins_score(application) * X2 * X3
        income_in_min = min(income, X0)
        return max(income_in_min, ins_score)
    else:
        salara_by_hour = salary_hour * X5 * X6 * X7
        income_in_min = min(income, X8 * X1)
        return max(income_in_min, salara_by_hour)

def __ma_score(ma):
    if ma <= 1000000:
        return 1
    if ma <= 2000000:
        return 2
    if ma <= 3500000:
        return 3
    if ma <= 5000000:
        return 3
    if ma <= 7500000:
        return 4
    if ma <= 10000000:
        return 4
    if ma > 10000000:
        return 5
    return 0

def calc_density(key, value):
    if key == "age":
        return value * 9.4/ 100
    if key == "employment":
        return value * 13.4/ 100
    if key == "marital":
        return value * 5/ 100
    if key == "gender":
        return value * 6.7/ 100
    if key == "ma":
        return value * 21/ 100
    if key == "product":
        return value * 17.8/ 100
    if key == "agent":
        return value * 10.0/ 100
    if key == "group_customer":
        return value * 16.7/ 100

def __ins_score(application):
    idNumber = application['LOS_customer']['idNumber']
    res = ApplicationService.social_insurance(idNumber)
    data = res['data']['sInfos']
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
    idNumber = application['LOS_customer']['idNumber']
    mobilePhone = application['LOS_customer_profile']['mobilePhone']
    res = ApplicationService.credit_score(idNumber, mobilePhone)
    data = res['data']
    return data['score']