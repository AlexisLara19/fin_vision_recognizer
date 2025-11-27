
from fastapi import APIRouter, HTTPException
from ..schemas import UserRequestModel, UserResponseModel
from ..database import User

router =  APIRouter(prefix='/users')

@router.post('', response_model=UserResponseModel)
async def create_user(user: UserRequestModel):

    # Intentamos obtener un registro existente
    if User.select().where(User.username == user.username).first():
        raise HTTPException(status_code=409, detail='El usuario ya existe')
   
    hash_password =  User.create_password(user.password)

    user = User.create(
        username=user.username,
        password=hash_password)
    
    return user 