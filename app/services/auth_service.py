from argon2 import exceptions
from extensions.extensions import ph # password hasher

def get_hash_password(password: str) -> str:
    return ph.hash(password=password)

def verify_password(hashed_password:str, password:str) -> bool:
    
    try:
        ph.verify(hashed_password, password)
    except (
        exceptions.VerifyMismatchError,
        exceptions.VerificationError,
        exceptions.InvalidHashError,
        ):
            return False
    else:
        return True

