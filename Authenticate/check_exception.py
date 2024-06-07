from beanie import PydanticObjectId
from fastapi import HTTPException, status

async def check_existence(database, obj_id:PydanticObjectId):
    obj = await database.get(obj_id)
    if not obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Object with supplied id doesn't exist"
        )
    return obj

async def check_directory(Cobj_id:PydanticObjectId, Pobj_ids):
    if str(Cobj_id) not in Pobj_ids:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="wrong directory"
        )
    return True

async def check_authority(id: PydanticObjectId, array):
    if str(id) not in array:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No authority to access"
        )
    return True

async def check_duplicate(database, key:str, value:str):
    if await database.find({key:value}):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Object with supplied {key} already exist"
        )
    return True


async def convert_id(database, id:str):
    body = await database.find({"id_":id})
    if not body:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Can't find object"
        )
    objid = body.id
    return objid