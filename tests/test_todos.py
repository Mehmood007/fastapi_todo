from fastapi import status

from main import app
from models import Todos
from routers.todos import current_user, get_db

from .utils import (
    TestingSessionLocal,
    client,
    override_current_user,
    override_get_db,
    test_todo,
)

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[current_user] = override_current_user


def test_get_all_todos(test_todo):
    response = client.get('/todos')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {
            'id': 1,
            'title': 'Test Title',
            'description': 'Test Description',
            'priority': 5,
            'complete': True,
            'owner_id': 1,
        }
    ]


def test_get_one_todos(test_todo):
    response = client.get('/todo/1')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        'id': 1,
        'title': 'Test Title',
        'description': 'Test Description',
        'priority': 5,
        'complete': True,
        'owner_id': 1,
    }


def test_get_one_todos_non_existing(test_todo):
    response = client.get('/todo/122')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'No todo found'}


def test_create_todo(test_todo):
    todo_data = {
        'id': 1,
        'title': 'Test Title',
        'description': 'Test Description',
        'priority': 5,
        'complete': True,
        'owner_id': 1,
    }
    response = client.post('/todos', json=todo_data)
    assert response.status_code == status.HTTP_201_CREATED


def test_update_todo(test_todo):
    todo_data = {
        'id': 1,
        'title': 'Updated title of already saved todo',
        'description': 'Updated Todo Description',
        'priority': 5,
        'complete': True,
        'owner_id': 1,
    }
    response = client.put('/todo/1', json=todo_data)
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert response.status_code == status.HTTP_200_OK
    assert model.title == 'Updated title of already saved todo'


def test_update_todo_not_found():
    todo_data = {
        'id': 1,
        'title': 'Updated title of already saved todo',
        'description': 'Updated Todo Description',
        'priority': 5,
        'complete': True,
        'owner_id': 1,
    }
    response = client.put('/todo/12', json=todo_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'No todo found'}


def test_delete_todo(test_todo):
    response = client.delete('/todo/1')
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert response.status_code == status.HTTP_200_OK
    assert model is None


def test_delete_todo_not_found():
    response = client.delete('/todo/12')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'No todo found'}
