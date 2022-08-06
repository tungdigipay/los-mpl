from repositories import CustomerRepository

def storage(request):
    dateOfBirth = request.dateOfBirth
    fullName = request.fullName
    genderID = request.genderID
    idNumber = request.idNumber

    return dateOfBirth
    return CustomerRepository.create(dateOfBirth, fullName, idNumber, genderID)