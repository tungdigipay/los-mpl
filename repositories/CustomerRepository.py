from libraries import Hasura

def create(dateOfBirth, fullName, idNumber, genderID):
    query = """
mutation m_insertCustomer { 
    insert_LOS_customers(
        objects: {
            dateOfBirth: "%s", 
            fullName: "%s", 
            idNumber: "%s", 
            genderID: "%d"
        }
    ) 
    { returning { ID UUID } } 
} 
""" % (dateOfBirth, fullName.upper(), idNumber, genderID)
    return Hasura.process("m_insertCustomer", query)