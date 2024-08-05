from datetime import datetime, timedelta, timezone
from typing import Annotated, Union

from decouple import config
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status

from database import SessionLocal
from models import Users

router = APIRouter(
    tags=['auth'],
)

SECRET_KEY = config('SECRET_KEY')
ALGORITHM = 'HS256'


bycrpt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
outh2_bearer = OAuth2PasswordBearer(tokenUrl='token')


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


class CreateUserRequest(BaseModel):
    email: str
    username: str
    first_name: str
    last_name: str
    password: str
    role: str
    phone_number: str


def authenticate(
    username: str,
    password: str,
    db: db_dependency,
) -> Union[bool, Users]:
    user = db.query(Users).filter(Users.username == username).first()

    if not user:
        return False
    if not bycrpt_context.verify(password, user.hashed_password):
        return False
    return user


async def current_user(token: Annotated[str, Depends(outh2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
        username: str = payload.get('sub')
        user_id: str = payload.get('id')
        if not (username and user_id):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid token',
            )
        return {'username': username, 'id': user_id}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token'
        )


@router.post('/auth', status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, user: CreateUserRequest):
    user_model = Users(
        email=user.email,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        hashed_password=bycrpt_context.hash(user.password),
        role=user.role,
        phone_number=user.phone_number,
        is_active=True,
    )

    db.add(user_model)
    db.commit()

    return user_model


def create_jwt(username: str, user_id: int, expire_delta: timedelta) -> bytes:
    encode = {'sub': username, 'id': user_id}
    expires = datetime.now(timezone.utc) + expire_delta
    encode.update({'exp': expires})

    return jwt.encode(encode, SECRET_KEY, ALGORITHM)


@router.post('/token', status_code=status.HTTP_200_OK)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: db_dependency,
):
    user = authenticate(form_data.username, form_data.password, db)
    if user:
        token = create_jwt(user.username, user.id, timedelta(minutes=20))
        return {'access_token': token, 'token_type': 'bearer'}

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid credentials'
    )
