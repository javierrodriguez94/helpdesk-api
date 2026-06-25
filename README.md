# Helpdesk API

A REST API for managing customer support tickets, built with Python and Django REST Framework.

## Features

- JWT authentication (register, login)
- Ticket management with priority levels and status tracking
- Agent assignment system
- Internal comments (only visible to agents)
- Automatic audit log of all ticket changes
- Swagger/OpenAPI interactive documentation
- Pagination on all list endpoints

## Tech Stack

- **Python 3.14** / **Django 6**
- **Django REST Framework** — API layer
- **SimpleJWT** — JWT authentication
- **drf-spectacular** — Auto-generated OpenAPI/Swagger docs
- **PostgreSQL** — Database
- **pytest** — Test suite

## Getting Started

### Prerequisites

- Python 3.12+
- PostgreSQL

### Installation

```bash
# Clone the repo
git clone https://github.com/your-username/helpdesk-api.git
cd helpdesk-api

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your database credentials

# Create the database
createdb helpdesk_dev

# Apply migrations
python manage.py migrate

# Create a superuser (admin)
python manage.py createsuperuser

# Start the server
python manage.py runserver
```

The API will be available at `http://localhost:8000`.

## API Documentation

Once the server is running, visit `http://localhost:8000/api/docs/`

## Project Structure

```
helpdesk-api/
├── config/          # Django project settings and URL routing
├── accounts/        # User model and authentication endpoints
├── tickets/         # Ticket, Comment, and AuditLog models and endpoints
├── requirements.txt
└── manage.py
```

## Ticket Lifecycle

```
OPEN → IN_PROGRESS → RESOLVED → CLOSED
OPEN → CLOSED
IN_PROGRESS → OPEN
RESOLVED → OPEN
```

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `SECRET_KEY` | Django secret key | — |
| `DEBUG` | Debug mode | `False` |
| `ALLOWED_HOSTS` | Comma-separated allowed hosts | `localhost` |
| `DB_NAME` | Database name | `helpdesk_dev` |
| `DB_USER` | Database user | — |
| `DB_PASSWORD` | Database password | — |
| `DB_HOST` | Database host | `localhost` |
| `DB_PORT` | Database port | `5432` |

## License

MIT
