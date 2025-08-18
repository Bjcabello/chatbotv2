import bcrypt
import hashlib
def hash_password(plain_password: str) -> str:
    return bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    # encode_password = plain_password.encode("utf-8")
    # hash256 = hashlib.sha256()
    # hash256.update(encode_password)
    # hashed_password = hash256.hexdigest()
    # return hashed_password

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
