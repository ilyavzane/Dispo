import bcrypt


# generating password hash that will be saved in database
def generate_hash(password: str) -> str:
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    return hashed_password.decode()
