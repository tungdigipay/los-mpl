from libraries import Hasura

def storage(request):
    dateOfBirth = request.dateOfBirth
    fullName = request.fullName
    genderID = request.genderID
    idNumber = request.idNumber

    query = 'mutation m_insertCustomer { insert_LOS_customers(objects: {dateOfBirth: "' + dateOfBirth + '", fullName: "' + fullName + '", idNumber: "' + idNumber + '", genderID: "' + str(genderID) + '"}) { returning { UUID } } } '
    return Hasura.process("m_insertCustomer", query)