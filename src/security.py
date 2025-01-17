import bcrypt
import jwt


SECRET_KEY = "somesecterkey"


def hash_password(password):
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password, hashed_password):
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))


def create_jwt_token(data):
    return jwt.encode(data, SECRET_KEY, algorithm="HS256")


def decode_jwt_token(token):
    return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
