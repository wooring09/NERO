from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from Models.users_m import User, update_user, sign_up
from Database.connection import Database
from Authenticate.hash_password import HashPassword
from Authenticate.authenticate import authenticate, create_token
from Authenticate.check_exception import check_existence, check_authority, check_directory, convert_id, check_duplicate

user_router = APIRouter()
user_database = Database(User)
hash_password = HashPassword()

@user_router.post("/signup")
async def signup(body: sign_up):
    await check_duplicate(user_database, "name", body.name)
    await check_duplicate(user_database, "displayname", body.displayname)

    user = User(**body.model_dump())
    user.password = hash_password.hash(user.password)
    await user_database.insert(user)
    return "successfully signed up"

@user_router.post("/signin")
async def signin(user: OAuth2PasswordRequestForm = Depends()):
    user_objid = await convert_id(user_database, user.username)
    user_exists = await check_existence(user_database, user_objid)
    
    if not hash_password.verify(user.password, user_exists.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="password is not correct"
        )
    token = create_token(user.username)
    return{
        "access_token": token,
        "token_type": "Bearer"
    }

@user_router.put("/update")
async def updateuser(body: update_user, user:str = Depends(authenticate)):
    user_objid = await convert_id(user_database, user)
    await check_duplicate(user_database, "name", body.name)
    await check_duplicate(user_database, "displayname", body.displayname)
    
    if body.password:
        body.password = hash_password.hash(body.password)
    await user_database.update(user_objid, body)
    return "successfully updated"

@user_router.delete("/resign")
async def resign(password:str, user:str = Depends(authenticate)):
    user_objid = await convert_id(user_database, user)
    user_exist = await check_existence(user_database, user_objid)
    pw_exist = user_exist.password
    if not hash_password.verify(password, pw_exist):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="password is not correct"
        )
    await user_database.deleteUser(user_objid)
    return "successfully resigned"    

@user_router.post("/{target_id}/follow")
async def followuser(target_id:str, user:str = Depends(authenticate)):
    user_objid = await convert_id(user_database, user)
    target_objid = await convert_id(user_database, target_id)
    target = await check_existence(user_database, target_objid)
    followers = target.followers
    if target_id == user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="can't follow yourself"
        )
    if str(user_objid) in followers:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="already followed"
        )
        
    await user_database.followUser(user_objid, target_objid)
    return "succesfully followed"

@user_router.post("/{target_id}/unfollow")
async def unfollowuser(target_id:str, user:str = Depends(authenticate)):
    user_objid = await convert_id(user_database, user)
    target_objid = await convert_id(user_database, target_id)
    target = await check_existence(user_database, target_objid)
    followers = target.followers
    if not str(user_objid) in followers:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="already unfollowed"
        )
    
    await user_database.unfollowUser(user_objid, target_objid)
    return "succesfully unfollowed"
