from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from Models.users_m import User
from Database.connection import Basic_connection, Users_coll
from Authenticate.hash_password import HashPassword
from Authenticate.authenticate import authenticate, create_token

user_router = APIRouter()
user_database = Basic_connection(Users_coll)
hash_password = HashPassword()

@user_router.post("/signup")
async def signup(user: User):
    if await user_database.findOne({"email":user.email}) != None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="user with the email already exists"
        )
    user.password = hash_password.hash(user.password)
    await user_database.insertOne(user)
    return "successfully signed up"
    

@user_router.post("/signin")
async def signin(user: OAuth2PasswordRequestForm = Depends(User)):
    user_exists = await user_database.findOne({"email":user.email})
    if not user_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="user is not found"
        )
    if not hash_password.verify(user.password, user_exists["password"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="password is not correct"
        )
    token = create_token(user_exists["email"])
    return{
        "token": token,
        "type": "Bearer"
    }
