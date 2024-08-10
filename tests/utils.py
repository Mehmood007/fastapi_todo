import pytest
from fastapi.testclient import TestClient
from passlib.context import CryptContext
from sqlalchemy import create_engine, text
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base
from main import app
from models import Todos, Users

SQLALCHEMY_DATABASE_URL = 'sqlite:///./test_todos.db'

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={'check_same_thread': False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base.metadata.create_all(bind=engine)
bycrpt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def override_current_user():
    return {
        'username': 'testuser',
        'id': 1,
        'role': 'admin',
        'email': 'testuser@email.com',
    }


client = TestClient(app)


@pytest.fixture
def test_todo():
    todo = Todos(
        title='Test Title',
        description='Test Description',
        priority=5,
        complete=True,
        owner_id=1,
    )

    db = TestingSessionLocal()
    db.add(todo)
    db.commit()

    yield todo

    with engine.connect() as connection:
        connection.execute(text('DELETE FROM todos;'))
        connection.commit()


@pytest.fixture
def test_user():
    user = Users(
        id=1,
        email='testuser1@email.com',
        username='testuser1',
        first_name='test',
        last_name='user',
        hashed_password=bycrpt_context.hash('password'),
        is_active=True,
        role='Basic',
        phone_number='+92 1234567890',
    )

    db = TestingSessionLocal()
    db.add(user)
    db.commit()

    yield user

    with engine.connect() as connection:
        connection.execute(text('DELETE FROM users;'))
        connection.commit()
