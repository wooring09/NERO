from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from Models.users_m import User, update_user, sign_up
from Database.connection import Database
from Authenticate.hash_password import HashPassword
from Authenticate.authenticate import authenticate, create_token

user_router = APIRouter()
user_database = Database(User)
hash_password = HashPassword()

@user_router.post("/signup")
async def signup(body: sign_up):
    if await user_database.find({"id_":body.id_}):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="user with the email already exists"
        )
    if await user_database.find({"name":body.name}):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="user with the name already exists"
        )
    user = User(**body.model_dump())

    user.password = hash_password.hash(user.password)
    await user_database.insert(user)
    return "successfully signed up"

@user_router.post("/signin")
async def signin(user: OAuth2PasswordRequestForm = Depends()):
    user_objid = await user_database.id_to_OBJid(user.username)
    user_exists = await user_database.get(user_objid)
    if not user_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="user is not found"
        )
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
    user_objid = await user_database.id_to_OBJid(user)

    if body.password:
        body.password = hash_password.hash(body.password)
    if await user_database.find({"id_":body.id_}):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="user with the id already exists"
        )
    if await user_database.find({"name":body.name}):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="user with the name already exists"
        )
    
    await user_database.update(user_objid, body)
    return "successfully updated"

@user_router.delete("/resign")
async def resign(password:str, user:str = Depends(authenticate)):
    user_exist = await user_database.find({"id_":user})
    pw_exist = user_exist.password
    if not hash_password.verify(password, pw_exist):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="password is not correct"
        )
    # user_database.deleteUser()
    # return "successfully resigned"
    return "not yet made"
    

@user_router.post("/{target_id}/follow")
async def followuser(target_id:str, user:str = Depends(authenticate)):
    user_objid = await user_database.id_to_OBJid(user)
    target_objid = await user_database.id_to_OBJid(target_id)

    target = await user_database.get(target_objid)
    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="user not found"
        )
    followers = target.followers

    if target_id == user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="can't follow yourself"
        )
    if str(user_objid) in followers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="already followed"
        )
        
    await user_database.followUser(user_objid, target_objid)
    return "succesfully followed"

@user_router.post("/{target_id}/unfollow")
async def unfollowuser(target_id:str, user:str = Depends(authenticate)):
    user_objid = await user_database.id_to_OBJid(user)
    target_objid = await user_database.id_to_OBJid(target_id)
    if not target_objid:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="user not found"
        )

    target = await user_database.get(target_objid)
    followers = target.followers
    if not str(user_objid) in followers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="already unfollowed"
        )
    await user_database.unfollowUser(user_objid, target_objid)
    return "succesfully unfollowed"
