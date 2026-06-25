import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def customer(db):
    return User.objects.create_user(username='customer1', password='password123', role='customer')


@pytest.fixture
def agent(db):
    return User.objects.create_user(username='agent1', password='password123', role='agent')


@pytest.fixture
def auth_client(client):
    def _auth(user):
        response = client.post('/api/v1/auth/login/', {'username': user.username, 'password': 'password123'})
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")
        return client
    return _auth
