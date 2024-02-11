create_user = {
    "username": "pepito",
    "password": "123456",
    "email": "pepito@gmail.com",
    "dni": "456543452",
    "fullName": "pepito Perez",
    "phoneNumber": "3124567890"
}

create_user_duplicated = {
    "username": "pepito",
    "password": "123456",
    "email": "pepito@gmail.com",
    "dni": "456543452",
    "fullName": "pepito Perez",
    "phoneNumber": "3124567890"
}

create_user_with_not_properties = {
    "fullName": "Maria Aguilar"
}

update_user_success = {
    "status": "VERIFICADO",
    "dni": "45242315346",
    "fullName": "Miguel Lopez",
    "phoneNumber": "3014649834"
}

update_user_not_properties = {
    "email": "mariano@yahoo.com"
}

generate_token = {
    "username": "pepito",
    "password": "123456"
}

generate_token_invalid_password = {
    "username": "pepito",
    "password": "123T456"
}

generate_token_no_user = {
    "username": "oscar",
    "password": "123456"
}

generate_token_no_properties = {
    "username": "maria",
}