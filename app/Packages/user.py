from argon2 import PasswordHasher, exceptions

class User:
    def __init__(self, username, hash_pw=None):
        self.username   = username
        self.hash_pw    = hash_pw
        self.ph         = PasswordHasher()
    
    def verify(self, pw) -> bool:
        try:
            self.ph.verify(hash=self.hash_pw, password=pw)
        except (
        exceptions.VerifyMismatchError,
        exceptions.VerificationError,
        exceptions.InvalidHashError,
        ):
            return False
        else:
            print("Login success")
            return True
    def generateHash(self, password):
        self.hash_pw = self.ph.hash(password)
        return self