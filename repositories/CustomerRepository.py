from libraries import Hasura

def create(dateOfBirth, fullName, idNumber, genderID):
    query = 'mutation m_insertCustomer { insert_LOS_customers(objects: {dateOfBirth: "' + dateOfBirth + '", fullName: "' + fullName + '", idNumber: "' + idNumber + '", genderID: "' + str(genderID) + '"}) { returning { UUID } } } '
    return Hasura.process("m_insertCustomer", query)