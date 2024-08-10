from fastapi import status

from main import app
from routers.users import current_user, get_db

from .utils import client, override_current_user, override_get_db, test_user

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[current_user] = override_current_user


def test_return_user(test_user):
    response = client.get('/users/')
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['email'] == 'testuser1@email.com'


def test_change_password(test_user):
    payload = {'password': 'password', 'new_password': 'UpdatedPassword'}
    response = client.put('/users/password', json=payload)

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_change_password_invalid(test_user):
    payload = {'password': 'wrong password', 'new_password': 'UpdatedPassword'}
    response = client.put('/users/password', json=payload)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()['detail'] == 'Not authorized'
