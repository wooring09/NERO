from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class HashPassword:
    def hash(self, password:str):
        return pwd_context.hash(password)
    def verify(self, password:str, hahsed_password: str):
        return pwd_context.verify(password, hahsed_password)