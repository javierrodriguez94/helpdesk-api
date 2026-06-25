import pytest
from django.contrib.auth import get_user_model
from tickets.models import Ticket

User = get_user_model()


@pytest.fixture
def ticket(db, customer):
    return Ticket.objects.create(
        subject='Test ticket',
        description='Test description',
        priority='medium',
        created_by=customer,
    )


@pytest.mark.django_db
def test_create_ticket(client, customer, auth_client):
    auth_client(customer)
    response = client.post('/api/v1/tickets/', {
        'subject': 'Mi problema',
        'description': 'Descripción del problema',
        'priority': 'high',
    })
    assert response.status_code == 201
    assert response.data['subject'] == 'Mi problema'
    assert response.data['status'] == 'open'


@pytest.mark.django_db
def test_unauthenticated_cannot_create_ticket(client):
    response = client.post('/api/v1/tickets/', {
        'subject': 'Test',
        'description': 'Test',
        'priority': 'low',
    })
    assert response.status_code == 401


@pytest.mark.django_db
def test_customer_only_sees_own_tickets(client, customer, agent, ticket, auth_client):
    other_customer = User.objects.create_user(username='customer2', password='password123', role='customer')
    Ticket.objects.create(subject='Other ticket', description='...', priority='low', created_by=other_customer)

    auth_client(customer)
    response = client.get('/api/v1/tickets/')
    assert response.status_code == 200
    assert response.data['count'] == 1


@pytest.mark.django_db
def test_agent_sees_all_tickets(client, customer, agent, ticket, auth_client):
    other_customer = User.objects.create_user(username='customer2', password='password123', role='customer')
    Ticket.objects.create(subject='Other ticket', description='...', priority='low', created_by=other_customer)

    auth_client(agent)
    response = client.get('/api/v1/tickets/')
    assert response.status_code == 200
    assert response.data['count'] == 2


@pytest.mark.django_db
def test_valid_status_transition(client, agent, ticket, auth_client):
    auth_client(agent)
    response = client.patch(f'/api/v1/tickets/{ticket.id}/set_status/', {'status': 'in_progress'})
    assert response.status_code == 200
    assert response.data['status'] == 'in_progress'


@pytest.mark.django_db
def test_invalid_status_transition(client, agent, ticket, auth_client):
    auth_client(agent)
    response = client.patch(f'/api/v1/tickets/{ticket.id}/set_status/', {'status': 'resolved'})
    assert response.status_code == 400


@pytest.mark.django_db
def test_customer_cannot_change_status(client, customer, ticket, auth_client):
    auth_client(customer)
    response = client.patch(f'/api/v1/tickets/{ticket.id}/set_status/', {'status': 'in_progress'})
    assert response.status_code == 403


@pytest.mark.django_db
def test_customer_cannot_assign_ticket(client, customer, agent, ticket, auth_client):
    auth_client(customer)
    response = client.patch(f'/api/v1/tickets/{ticket.id}/assign/', {'assigned_to': agent.id})
    assert response.status_code == 403


@pytest.mark.django_db
def test_assign_ticket(client, agent, ticket, auth_client):
    auth_client(agent)
    response = client.patch(f'/api/v1/tickets/{ticket.id}/assign/', {'assigned_to': agent.id})
    assert response.status_code == 200
    assert response.data['assigned_to'] == str(agent)


@pytest.mark.django_db
def test_assign_to_nonexistent_user(client, agent, ticket, auth_client):
    auth_client(agent)
    response = client.patch(f'/api/v1/tickets/{ticket.id}/assign/', {'assigned_to': 9999})
    assert response.status_code == 400


@pytest.mark.django_db
def test_assign_to_customer_fails(client, agent, customer, ticket, auth_client):
    auth_client(agent)
    response = client.patch(f'/api/v1/tickets/{ticket.id}/assign/', {'assigned_to': customer.id})
    assert response.status_code == 400


@pytest.mark.django_db
def test_add_comment(client, agent, ticket, auth_client):
    auth_client(agent)
    response = client.post(f'/api/v1/tickets/{ticket.id}/comments/', {'body': 'Revisando el problema'})
    assert response.status_code == 201
    assert response.data['body'] == 'Revisando el problema'


@pytest.mark.django_db
def test_customer_cannot_see_other_ticket_comments(client, customer, auth_client):
    other_customer = User.objects.create_user(username='customer2', password='password123', role='customer')
    other_ticket = Ticket.objects.create(subject='Other', description='...', priority='low', created_by=other_customer)

    auth_client(customer)
    response = client.get(f'/api/v1/tickets/{other_ticket.id}/comments/')
    assert response.status_code == 404


@pytest.mark.django_db
def test_customer_cannot_see_other_ticket_history(client, customer, auth_client):
    other_customer = User.objects.create_user(username='customer2', password='password123', role='customer')
    other_ticket = Ticket.objects.create(subject='Other', description='...', priority='low', created_by=other_customer)

    auth_client(customer)
    response = client.get(f'/api/v1/tickets/{other_ticket.id}/history/')
    assert response.status_code == 404


@pytest.mark.django_db
def test_status_change_creates_audit_log(client, agent, ticket, auth_client):
    auth_client(agent)
    client.patch(f'/api/v1/tickets/{ticket.id}/set_status/', {'status': 'in_progress'})
    response = client.get(f'/api/v1/tickets/{ticket.id}/history/')
    assert response.status_code == 200
    assert response.data['count'] == 1
    assert response.data['results'][0]['field'] == 'status'
    assert response.data['results'][0]['old_value'] == 'open'
    assert response.data['results'][0]['new_value'] == 'in_progress'
