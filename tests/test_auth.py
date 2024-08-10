from datetime import timedelta

import pytest
from fastapi import HTTPException
from jose import jwt

from main import app
from routers.auth import (
    ALGORITHM,
    SECRET_KEY,
    authenticate,
    create_jwt,
    current_user,
    get_db,
)

from .utils import TestingSessionLocal, override_get_db, test_user

app.dependency_overrides[get_db] = override_get_db


def test_authenticate_user(test_user):
    db = TestingSessionLocal()

    authenticated_user = authenticate(test_user.username, 'password', db)

    assert test_user.email == authenticated_user.email


def test_wrong_password(test_user):
    db = TestingSessionLocal()

    authenticated_user = authenticate(test_user.username, 'wrong password', db)

    assert authenticated_user is False


def test_create_jwt():
    username = 'testuser'
    user_id = 1
    expire_delta = timedelta(days=1)

    token = create_jwt(username, user_id, expire_delta)

    decoded_token = jwt.decode(
        token, SECRET_KEY, algorithms=[ALGORITHM], options={'verify_signature': False}
    )

    assert decoded_token['sub'] == username
    assert decoded_token['id'] == user_id


@pytest.mark.asyncio
async def test_get_current_user_valid_token():
    encode = {'sub': 'testuser', 'id': 1}

    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
    user = await current_user(token)

    assert user == {'username': 'testuser', 'id': 1}


@pytest.mark.asyncio
async def test_get_current_missing_payload():
    encode = {'sub': 'testuser'}

    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

    with pytest.raises(HTTPException) as execinfo:
        await current_user(token)

    assert execinfo.value.status_code == 401
