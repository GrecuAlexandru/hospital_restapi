# Hospital REST API

A RESTful API for hospital management.

## Getting Started

### Prerequisites

- Python 3.8 or higher (I used Python 3.12.3)
- SQLite (included in Python)
- Git

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/GrecuAlexandru/hospital_restapi.git
   cd hospital_restapi
   ```

2. Create a virtual environment (recommended) (I used WSL):
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. Install the required dependencies:
   ```bash
   pip install fastapi uvicorn[standard] pydantic[email] sqlalchemy passlib==1.7.4 bcrypt==4.0.1 python-multipart httpx
   ```

## Usage

### Starting the Server

To start the API server with an empty database:
```bash
python run.py
```

To start the server with sample data (fixtures):
```bash
python run.py --with-fixtures
```

The API will be available at http://localhost:8000

### Example Requests

#### Login (This will work only if you have the fixtures)
```bash
curl -X POST "http://localhost:8000/login" -d "email=admin@hospital.com&password=admin123" -H "Content-Type: application/x-www-form-urlencoded"
```

#### Get All Doctors (as admin)
```bash
curl -X GET "http://localhost:8000/doctors/?current_user_email=admin@hospital.com"
```

#### Create a New Patient (as admin)
```bash
curl -X POST "http://localhost:8000/patients/?current_user_email=admin@hospital.com" \
  -H "Content-Type: application/json" \
  -d '{"first_name": "John", "last_name": "Doe", "age": 45}'
```

## Database

The application uses SQLite by default. The database file (`hospital.db`) will be created automatically in the project root directory the first time you run the application.

## Testing

Run the tests to verify the API functionality:

```bash
# Run specific test modules (in a new terminal)
python tests/test_assistant.py
python tests/test_basic.py
python tests/test_doctor.py
python tests/test_fixtures.py
python tests/test_patient.py
python tests/test_reports.py
python tests/test_treatment.py
```

## Security Vulnerabilities

### 1. Authentication Vulnerabilities

#### Email-Based Authentication using Query Parameters

The API authenticates users using email passed as query parameters. This is highly insecure because:
- Query parameters appear in URLs, server logs, and browser history
- No tokens or secure session management is implemented
- Authentication is optional in many endpoints (current_user_email is optional)

Solution: Implement token-based authentication (JWT) with proper expiration and refresh mechanisms.

#### Weak Password Security Controls

While passwords are hashed using bcrypt, the system lacks:
- Password complexity requirements
- Rate limiting for login attempts

### 2. Authorization Issues

#### Inconsistent Permission Checks

Many endpoints have conditional permission checks:
- These checks are bypassed if current_user_email is not provided.

### 3. Data Security Issues

#### Excessive Data Exposure

Many endpoints return complete objects rather than necessary fields.

### 4. API Security Issues

#### Missing Rate Limiting

The API has no protection against excessive requests, making it vulnerable to DoS attacks and brute force attempts.