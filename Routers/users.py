from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm

from authenticate.hash_password import HashPassword
from authenticate.authenticate import authenticate, create_token
from database.connection import UserCol

from models.users import (
    User,
    UpdateUser, 
    SignUp,
    ReturnUserPassword
)


user_router = APIRouter()
hash_password = HashPassword()


@user_router.post("/signup")
async def signup(body: SignUp) -> dict:

    await UserCol.check_duplicate(
        UserCol.name==body.name,
        message="username with supplied user_name already exists"
    )

    user = UserCol(**body.model_dump())
    user.password = hash_password.hash_password(user.password)

    await user.create()
    return {
        "message": "user signed up successfully"
    }

#
#
#

@user_router.post("/signin")
async def signin(user: OAuth2PasswordRequestForm = Depends()) -> dict:

    user_doc = await UserCol.check_existence_and_return(
        UserCol.name==user.username,
        obj_type="User",
        project=ReturnUserPassword
    )
    
    if not hash_password.verify_password(user.password, user_doc.password):
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

#
# 이쪽 밑에껀 follow, unfollow 잘 구현 안되어 있음.
#

# @user_router.put("/update")
# async def updateuser(body: UpdateUser, user:str = Depends(authenticate)):
#     user_exist = await check_existence(user_database, user)
#     await check_duplicate(user_database, "name", body.name)
#     await check_duplicate(user_database, "displayname", body.displayname)
    
#     if body.password:
#         body.password = hash_password.hash_password(body.password)
#     await user_database.update(user_exist.id, body)
#     return "successfully updated"

@user_router.put("/update")
async def update_user(body: UpdateUser, 
                      user: str = Depends(authenticate)) -> dict:
    
    user_exist = await UserCol.check_existence_and_return(
        UserCol.name == user,
        obj_type="User"
    )


    await UserCol.check_duplicate(
        UserCol.name == body.name,
        obj_type="User"
    )

    if body.password:
        body.password = hash_password.hash_password(body.password)

    await UserCol.vanish_none_and_update(user_exist, body)
    return {"message": "successfully updated"}

# @user_router.delete("/resign")
# async def resign(password:str, user:str = Depends(authenticate)):
#     user_exist = await check_existence_with_name(user_database, user)
#     pw_exist = user_exist.password
#     if not hash_password.verify_password(password, pw_exist):
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="password is not correct"
#         )
#     await user_database.deleteUser(user_exist.id)
#     return "successfully resigned"    

@user_router.delete("/resign")
async def resign(password: str, 
                 user: str = Depends(authenticate)) -> dict:
    
    user_exist = await UserCol.check_existence_and_return(
        UserCol.name == user,
        message="user with supplied username doesn't exist"
    )

    if not hash_password.verify_password(password, user_exist.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="password is not correct"
        )

    await user_exist.delete()
    return {"message": "successfully resigned"}

# @user_router.post("/{target_name}/follow")
# async def followuser(target_name:str, user:str = Depends(authenticate)):
#     target = await check_existence_with_name(user_database, target_name)
#     followers = target.followers
#     if target_name == user:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="can't follow yourself"
#         )
#     if user in followers:
#         raise HTTPException(
#             status_code=status.HTTP_409_CONFLICT,
#             detail="already followed"
#         )
        
#     await user_database.followUser(user, target_name)
#     return "succesfully followed"

@user_router.post("/{target_name}/follow")
async def follow_user(target_name: str, 
                      user: str = Depends(authenticate)) -> dict:
    
    target = await UserCol.check_existence_and_return(
        UserCol.name == target_name,
        message="user with supplied username doesn't exist"
    )

    if target_name == user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="can't follow yourself"
        )

    if user in target.followers:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="already followed"
        )

    target.followers.append(user)
    await target.save()
    return {"message": "successfully followed"}


# @user_router.post("/{target_name}/unfollow")
# async def unfollowuser(target_name:str, user:str = Depends(authenticate)):
#     target = await check_existence_with_name(user_database, target_name)
#     followers = target.followers
#     if not user in followers:
#         raise HTTPException(
#             status_code=status.HTTP_409_CONFLICT,
#             detail="already unfollowed"
#         )
    
#     await user_database.unfollowUser(user, target_name)
#     return "succesfully unfollowed"

@user_router.post("/{target_name}/unfollow")
async def unfollow_user(target_name: str, 
                        user: str = Depends(authenticate)) -> dict:
    
    target = await UserCol.check_existence_and_return(
        UserCol.name == target_name,
        message="user with supplied username doesn't exist"
    )

    if user not in target.followers:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="already unfollowed"
        )

    target.followers.remove(user)
    await target.save()
    return {"message": "successfully unfollowed"}
