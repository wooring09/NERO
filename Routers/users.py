from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from Models.users_m import User, updateUser
from Database.connection import Database, Users_coll
from Authenticate.hash_password import HashPassword
from Authenticate.authenticate import authenticate, create_token

user_router = APIRouter()
user_database = Database(Users_coll)
hash_password = HashPassword()

@user_router.post("/signup")
async def signup(user: User):
    if await user_database.findOne({"email":user.email}):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="user with the email already exists"
        )
    if await user_database.findOne({"name":user.name}):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="user with the name already exists"
        )
    user.password = hash_password.hash(user.password)
    user.followers = []
    user.followingUsers = []
    user.followingBooks = []
    await user_database.insertOne(user)
    return "successfully signed up"

@user_router.post("/signin")
async def signin(user: OAuth2PasswordRequestForm = Depends()):
    user_exists = await user_database.findOne({"email":user.username})
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
        "access_token": token,
        "token_type": "Bearer"
    }

@user_router.put("/update")
async def updateuser(data: updateUser, user:str = Depends(authenticate)):
    if await user_database.findOne({"name":data.name}):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="user with the name already exists"
        )
    await user_database.updateOne({"email":user}, data)
    return "successfully updated"

@user_router.delete("/resign")
async def resign(password, user:str = Depends(authenticate)):
    pw_exist = dict(await user_database.findOne({"email":user}))["password"]
    if not hash_password.verify(password, pw_exist):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="password is not correct"
        )
    # user_database.deleteUser()
    # return "successfully resigned"
    return "not yet made"
    

@user_router.post("/{name}/follow")
async def followuser(name, user:str = Depends(authenticate)):
    target = await user_database.findOne({"name":name})
    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="user not found"
        )
    email = dict(target)["email"]
    followers = dict(await user_database.findOne({"email":user}))["followers"]
    if email == user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="can't follow yourself"
        )
    if email in followers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="already followed"
        )
        
    await user_database.followUser(user, email)
    return "succesfully followed"

@user_router.post("/{name}/unfollow")
async def unfollowuser(name, user:str = Depends(authenticate)):
    target = await user_database.findOne({"name":name})
    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="user not found"
        )
    email = dict(target)["email"]
    following = dict(await user_database.findOne({"email":user}))["followingUsers"]
    if not email in following:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="already unfollowed"
        )
    await user_database.unfollowUser(user, email)
    return "succesfully unfollowed"
