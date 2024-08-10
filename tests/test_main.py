from fastapi import status
from fastapi.testclient import TestClient

import main

client = TestClient(main.app)


def test_return_health_check():
    response = client.get('/')  # empty string main root url
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'message': 'System is up and running'}
