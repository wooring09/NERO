from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from models.users import User, update_user, sign_up
from database.connection import Database, UserCol
from authenticate.hash_password import HashPassword
from authenticate.authenticate import authenticate, create_token
from database.exception_handler import check_existence, check_authority, check_directory, check_duplicate, check_existence_with_name

user_router = APIRouter()
user_database = Database(User)
hash_password = HashPassword()

@user_router.post("/signup")
async def signup(body: sign_up) -> dict:
    # await check_duplicate(user_database, "name", body.name)
    await UserCol.check_duplicate(
        UserCol.name==body.name,
        message="username with supplied user_name already exists"
    )

    user = UserCol(**body.model_dump())
    user.password = hash_password.hash(user.password)
    # await user_database.insert(user)
    await user.create()
    return {
        "message": "user signed up successfully"
    }

@user_router.post("/signin")
async def signin(user: OAuth2PasswordRequestForm = Depends()) -> dict:
    # user_exists = await check_existence_with_name(user_database, user.username)

    user = await UserCol.check_existence_and_return_document(
        UserCol.name==user.username,
        message="user with supplied username doesn't exists",
        project=UserCol.password
    )
    
    if not hash_password.verify(user.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail= {
                "message": "password is not correct"
            }
        )
    
    token = create_token(user.username)
    
    return {
        "access_token": token,
        "token_type": "Bearer"
    }

@user_router.put("/update")
async def updateuser(body: update_user, user:str = Depends(authenticate)):
    user_exist = await check_existence(user_database, user)
    await check_duplicate(user_database, "name", body.name)
    await check_duplicate(user_database, "displayname", body.displayname)
    
    if body.password:
        body.password = hash_password.hash(body.password)
    await user_database.update(user_exist.id, body)
    return "successfully updated"

@user_router.delete("/resign")
async def resign(password:str, user:str = Depends(authenticate)):
    user_exist = await check_existence_with_name(user_database, user)
    pw_exist = user_exist.password
    if not hash_password.verify(password, pw_exist):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="password is not correct"
        )
    await user_database.deleteUser(user_exist.id)
    return "successfully resigned"    

@user_router.post("/{target_name}/follow")
async def followuser(target_name:str, user:str = Depends(authenticate)):
    target = await check_existence_with_name(user_database, target_name)
    followers = target.followers
    if target_name == user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="can't follow yourself"
        )
    if user in followers:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="already followed"
        )
        
    await user_database.followUser(user, target_name)
    return "succesfully followed"

@user_router.post("/{target_name}/unfollow")
async def unfollowuser(target_name:str, user:str = Depends(authenticate)):
    target = await check_existence_with_name(user_database, target_name)
    followers = target.followers
    if not user in followers:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="already unfollowed"
        )
    
    await user_database.unfollowUser(user, target_name)
    return "succesfully unfollowed"
