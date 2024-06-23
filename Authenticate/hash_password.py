from passlib.context import CryptContext
import bcrypt

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class HashPassword:
    # def hash_password(self, password:str):
    #     return pwd_context.hash(password)
    # def verify_password(self, password:str, hahsed_password: str):
    #     return pwd_context.verify(password, hahsed_password)

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hashes a password using bcrypt.
        
        Args:
            password (str): The plain text password to hash.
        
        Returns:
            str: The hashed password.
        """
        pwd_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)
        return hashed_password.decode('utf-8')  # Convert bytes to string for storage
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verifies a plain text password against a hashed password.
        
        Args:
            plain_password (str): The plain text password to verify.
            hashed_password (str): The hashed password to verify against.
        
        Returns:
            bool: True if the password matches, False otherwise.
        """
        password_byte_enc = plain_password.encode('utf-8')
        hashed_password_bytes = hashed_password.encode('utf-8')  # Convert string to bytes for verification
        return bcrypt.checkpw(password=password_byte_enc, hashed_password=hashed_password_bytes)