# Real Estate CRM - Backend Setup Guide

## 🚀 Quick Start

### Prerequisites
- **Python** 3.8+ (Python 3.10 recommended)
- **pip** (Python package manager)
- **PostgreSQL** or **SQLite** (for development)
- **Git** (for version control)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd real-estate-backend
```

2. **Create virtual environment**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Environment Configuration**
Create a `.env` file in the root directory:
```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (SQLite for development)
DATABASE_ENGINE=django.db.backends.sqlite3
DATABASE_NAME=db.sqlite3

# For PostgreSQL (production)
# DATABASE_ENGINE=django.db.backends.postgresql
# DATABASE_NAME=real_estate_db
# DATABASE_USER=postgres
# DATABASE_PASSWORD=your_password
# DATABASE_HOST=localhost
# DATABASE_PORT=5432

# CORS Settings
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# JWT Settings
JWT_ACCESS_TOKEN_LIFETIME=60  # minutes
JWT_REFRESH_TOKEN_LIFETIME=1440  # minutes (24 hours)
```

5. **Run migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Create superuser (admin)**
```bash
python manage.py createsuperuser
```

7. **Start development server**
```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000`

---

## 📁 Project Structure

```
real-estate-backend/
├── config/                 # Project configuration
│   ├── settings.py        # Django settings
│   ├── urls.py            # Main URL configuration
│   └── wsgi.py            # WSGI configuration
├── accounts/              # User management app
│   ├── models.py          # User, Employee models
│   ├── views.py           # Authentication views
│   ├── serializers.py     # API serializers
│   └── urls.py            # Account routes
├── leads/                 # Leads management app
│   ├── models.py          # Lead, LeadNote, Notification models
│   ├── views.py           # Lead CRUD views
│   ├── contact_views.py   # Contact form handlers
│   ├── notification_views.py  # Notification endpoints
│   └── urls.py            # Lead routes
├── properties/            # Properties management app
│   ├── models.py          # Property, PropertyType models
│   ├── views.py           # Property CRUD views
│   └── urls.py            # Property routes
├── manage.py              # Django management script
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (create this)
└── db.sqlite3            # SQLite database (auto-generated)
```

---

## 🗄️ Database Models

### User & Authentication
- **User** - Custom user model (email-based auth)
- **Employee** - Staff/Agent profiles linked to User

### Leads Management
- **Lead** - Customer lead information
- **LeadSource** - Lead source tracking
- **LeadNote** - Notes/comments on leads
- **Notification** - Real-time notifications

### Properties
- **Property** - Property listings
- **PropertyType** - Property categories
- **PropertyImage** - Property photos

### Scheduling
- **ScheduledVisit** - Property visit appointments

---

## 🛠️ Available Commands

### Development
```bash
python manage.py runserver          # Start dev server
python manage.py runserver 0.0.0.0:8000  # Accessible from network
```

### Database
```bash
python manage.py makemigrations     # Create migrations
python manage.py migrate            # Apply migrations
python manage.py createsuperuser    # Create admin user
python manage.py flush              # Clear database
python manage.py dbshell            # Open database shell
```

### Django Shell
```bash
python manage.py shell              # Python shell with Django
python manage.py shell_plus         # Enhanced shell (if installed)
```

### Static Files
```bash
python manage.py collectstatic      # Collect static files for production
```

---

## 🔐 API Endpoints

### Authentication
```
POST   /api/accounts/register/          # User registration
POST   /api/accounts/login/             # Login (JWT)
POST   /api/accounts/token/refresh/     # Refresh JWT token
GET    /api/accounts/profile/           # Get user profile
PUT    /api/accounts/profile/update/    # Update profile
```

### Leads
```
GET    /api/leads/list/                 # List all leads
POST   /api/leads/create/               # Create new lead
GET    /api/leads/<id>/                 # Get lead details
PATCH  /api/leads/<id>/update/          # Update lead
DELETE /api/leads/<id>/delete/          # Delete lead
GET    /api/leads/agents/               # List all agents
```

### Properties
```
GET    /api/properties/list/            # List all properties
POST   /api/properties/create/          # Create property
GET    /api/properties/detail/<id>/     # Property details
PATCH  /api/properties/<id>/update/     # Update property
DELETE /api/properties/<id>/delete/     # Delete property
GET    /api/properties/types/           # Property types
```

### Notifications
```
GET    /api/leads/notifications/        # Get user notifications
POST   /api/leads/notifications/mark-read/  # Mark as read
POST   /api/leads/notifications/mark-all-read/  # Mark all as read
DELETE /api/leads/notifications/<id>/delete/  # Delete notification
```

### Contact Forms (Public)
```
POST   /api/leads/contact/              # General contact form
POST   /api/leads/schedule-call/        # Schedule a call
POST   /api/leads/property-inquiry/     # Property-specific inquiry
```

### Scheduled Visits
```
GET    /api/leads/visits/               # List visits
POST   /api/leads/visits/create/        # Schedule visit
DELETE /api/leads/visits/<id>/delete/   # Cancel visit
```

---

## 🔧 Technology Stack

- **Django 4.2+** - Web framework
- **Django REST Framework** - API framework
- **SimpleJWT** - JWT authentication
- **django-cors-headers** - CORS handling
- **python-dotenv** - Environment variables
- **Pillow** - Image processing
- **SQLite/PostgreSQL** - Database

---

## 🔑 Authentication

The API uses **JWT (JSON Web Tokens)** for authentication:

1. **Login** → Receives `access` and `refresh` tokens
2. **Include token** in request headers:
   ```
   Authorization: Bearer <access_token>
   ```
3. **Token refresh** when expired using refresh token
4. **Protected routes** require valid JWT token

**User Roles & Permissions:**
- **Superuser** - Full admin access
- **Staff (is_staff=True)** - Admin dashboard access
- **Employee (is_employee=True)** - Agent access
- **Regular User (is_client=True)** - Customer access

---

## 🌐 CORS Configuration

CORS is configured to allow requests from the frontend:
- Development: `http://localhost:3000`
- Production: Add your domain to `CORS_ALLOWED_ORIGINS` in `.env`

---

## 📊 Admin Panel

Django Admin is available at `http://localhost:8000/admin/`

**Features:**
- Manage users, employees, leads
- View and edit properties
- Monitor notifications
- Database management

---

## 🐛 Troubleshooting

### Port already in use
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

### Database errors
```bash
# Reset database (WARNING: Deletes all data)
python manage.py flush
python manage.py migrate
```

### Module import errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Migration issues
```bash
# Delete migrations and recreate
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc"  -delete
python manage.py makemigrations
python manage.py migrate
```

---

## 🔄 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | Required |
| `DEBUG` | Debug mode | `True` |
| `ALLOWED_HOSTS` | Allowed host names | `localhost,127.0.0.1` |
| `DATABASE_ENGINE` | Database backend | `django.db.backends.sqlite3` |
| `DATABASE_NAME` | Database name | `db.sqlite3` |
| `CORS_ALLOWED_ORIGINS` | Frontend URLs | `http://localhost:3000` |
| `JWT_ACCESS_TOKEN_LIFETIME` | Access token lifetime (minutes) | `60` |
| `JWT_REFRESH_TOKEN_LIFETIME` | Refresh token lifetime (minutes) | `1440` |

---

## 📦 Deployment

### Production Checklist
1. Set `DEBUG=False` in `.env`
2. Configure `ALLOWED_HOSTS` with your domain
3. Use PostgreSQL instead of SQLite
4. Set strong `SECRET_KEY`
5. Configure static files serving
6. Set up HTTPS
7. Configure CORS for production domain
8. Run `collectstatic` for static files

### Using Gunicorn (Production Server)
```bash
pip install gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

### Using Docker
```dockerfile
# Example Dockerfile
FROM python:3.10
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
```

---

## 🧪 Testing

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test accounts
python manage.py test leads
python manage.py test properties

# Generate coverage report
coverage run --source='.' manage.py test
coverage report
```

---

## 📝 API Documentation

### Swagger/OpenAPI
Install `drf-yasg` for automatic API documentation:
```bash
pip install drf-yasg
```

Access docs at:
- Swagger UI: `http://localhost:8000/swagger/`
- ReDoc: `http://localhost:8000/redoc/`

---

## 👥 Development Guidelines

1. **Models** - Define database schema in `models.py`
2. **Views** - API logic in `views.py` or separate view files
3. **Serializers** - Data validation and serialization
4. **URLs** - Route configuration in `urls.py`
5. **Permissions** - Use DRF permission classes
6. **Signals** - Auto-create notifications using Django signals

---

## 📝 License

This project is proprietary software for the Real Estate CRM platform.

---

## 📞 Support

For issues or questions, contact the development team.
