import pytest
from django.contrib.auth import get_user_model


@pytest.mark.django_db
def test_register(client):
    response = client.post('/api/v1/auth/register/', {
        'username': 'newuser',
        'email': 'new@test.com',
        'password': 'password123',
    })
    assert response.status_code == 201
    assert response.data['username'] == 'newuser'
    assert 'password' not in response.data


@pytest.mark.django_db
def test_register_cannot_self_assign_admin_role(client):
    response = client.post('/api/v1/auth/register/', {
        'username': 'hacker',
        'email': 'hacker@test.com',
        'password': 'password123',
        'role': 'admin',
    })
    assert response.status_code == 201
    user = get_user_model().objects.get(username='hacker')
    assert user.role == 'customer'


@pytest.mark.django_db
def test_login(client, customer):
    response = client.post('/api/v1/auth/login/', {
        'username': 'customer1',
        'password': 'password123',
    })
    assert response.status_code == 200
    assert 'access' in response.data


@pytest.mark.django_db
def test_login_wrong_password(client, customer):
    response = client.post('/api/v1/auth/login/', {
        'username': 'customer1',
        'password': 'wrongpassword',
    })
    assert response.status_code == 401
