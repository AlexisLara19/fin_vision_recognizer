import jwt
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
from .database import User

SECRET_KEY = 'AirtempDeMexico2025'

oauth2_schema = OAuth2PasswordBearer(tokenUrl = '/api/v1/auth')  # Que hace esto?

def create_access_token(user, days_=7):
    
    data = {
        'user_id': user.id,
        'username': user.username,
        'exp':datetime.utcnow() + timedelta(days=days_)  # caducidad del token
    }

    return jwt.encode(data, SECRET_KEY, algorithm='HS256')

def decode_access_token(token: str):
    try: 
        return jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    except Exception as err:
        return None

def get_current_user(token: str = Depends(oauth2_schema)) -> User:
    data = decode_access_token(token)
    if data:
        return User.select().where(User.id==data['user_id']).first()
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail= 'Access Token no valido',
            headers= {'WWW.Autenticate': 'Bearer'}
        )
