def authenticate(username, password):

    VALID_USERNAME = "admin"
    VALID_PASSWORD = "admin"

    return (
        username == VALID_USERNAME
        and password == VALID_PASSWORD
    )