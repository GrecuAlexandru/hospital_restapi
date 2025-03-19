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
   pip install -r requirements.txt
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

## API Documentation

### Authentication Endpoints

- **POST /login**: Authenticate user
  - Form data: `email`, `password`
  - Returns user information if authentication is successful

- **GET /me**: Get current user information
  - Query parameter: `email`
  - Returns authenticated user details

### Doctor Endpoints

- **GET /doctors/**: Get all doctors
  - Query parameters: `skip`, `limit`, `current_user_email`
  - Access limited to general managers

- **POST /doctors/**: Create a new doctor
  - Body: DoctorCreate schema
  - Query parameter: `current_user_email`
  - Access limited to general managers

- **GET /doctors/{doctor_id}**: Get specific doctor
  - Path parameter: `doctor_id`
  - Query parameter: `current_user_email`
  - Access limited to general managers

- **PUT /doctors/{doctor_id}**: Update doctor information
  - Path parameter: `doctor_id`
  - Body: DoctorUpdate schema
  - Query parameter: `current_user_email`
  - Access limited to general managers

- **DELETE /doctors/{doctor_id}**: Delete (deactivate) a doctor
  - Path parameter: `doctor_id`
  - Query parameter: `current_user_email`
  - Access limited to general managers

### Patient Endpoints

- **GET /patients/**: Get all patients
  - Query parameters: `skip`, `limit`, `current_user_email`
  - Access limited to doctors and general managers

- **POST /patients/**: Create a new patient
  - Body: PatientCreate schema
  - Query parameter: `current_user_email`
  - Access limited to doctors and general managers

- **GET /patients/{patient_id}**: Get specific patient
  - Path parameter: `patient_id`
  - Query parameter: `current_user_email`
  - Access limited to doctors and general managers

- **PUT /patients/{patient_id}**: Update patient information
  - Path parameter: `patient_id`
  - Body: PatientUpdate schema
  - Query parameter: `current_user_email`
  - Access limited to doctors and general managers

- **DELETE /patients/{patient_id}**: Delete (deactivate) a patient
  - Path parameter: `patient_id`
  - Query parameter: `current_user_email`
  - Access limited to doctors and general managers

### Assistant Endpoints

- **GET /assistants/**: Get all assistants
  - Query parameters: `skip`, `limit`, `current_user_email`
  - Access limited to general managers

- **POST /assistants/**: Create a new assistant
  - Body: AssistantCreate schema
  - Query parameter: `current_user_email`
  - Access limited to general managers

- **GET /assistants/{assistant_id}**: Get specific assistant
  - Path parameter: `assistant_id`
  - Query parameter: `current_user_email`
  - Access limited to general managers

- **PUT /assistants/{assistant_id}**: Update assistant information
  - Path parameter: `assistant_id`
  - Body: AssistantUpdate schema
  - Query parameter: `current_user_email`
  - Access limited to general managers

- **DELETE /assistants/{assistant_id}**: Delete (deactivate) an assistant
  - Path parameter: `assistant_id`
  - Query parameter: `current_user_email`
  - Access limited to general managers

- **GET /assistants/patients/assignments**: Get patient-assistant assignments
  - Query parameters: `patient_id`, `assistant_id`, `current_user_email`
  - Assistants can only view their own assignments

- **POST /assistants/patients/assign**: Assign patient to assistant
  - Body: PatientAssistantCreate schema
  - Query parameter: `current_user_email`
  - Access limited to doctors and general managers

- **PUT /assistants/patients/assignments/{assignment_id}**: Update assignment
  - Path parameter: `assignment_id`
  - Body: PatientAssistantUpdate schema
  - Query parameter: `current_user_email`
  - Access limited to doctors and general managers

- **POST /assistants/treatments/apply**: Record treatment application
  - Body: TreatmentApplicationCreate schema
  - Query parameter: `current_user_email`
  - Access limited to assistants

- **GET /assistants/treatments/applications**: Get treatment applications
  - Query parameters: `treatment_id`, `assistant_id`, `current_user_email`
  - Assistants can only see their own applications

### Treatment Endpoints

- **POST /treatments/**: Create a new treatment
  - Body: TreatmentCreate schema
  - Query parameter: `current_user_email`
  - Doctors can only create treatments for their patients

- **GET /treatments/**: Get all treatments
  - Query parameters: `patient_id`, `doctor_id`, `skip`, `limit`, `current_user_email`
  - Filtered based on user role

- **GET /treatments/{treatment_id}**: Get specific treatment
  - Path parameter: `treatment_id`
  - Query parameter: `current_user_email`
  - Access controlled based on user role

- **PUT /treatments/{treatment_id}**: Update treatment
  - Path parameter: `treatment_id`
  - Body: TreatmentUpdate schema
  - Query parameter: `current_user_email`
  - Doctors can only update their treatments

- **DELETE /treatments/{treatment_id}**: Delete a treatment
  - Path parameter: `treatment_id`
  - Query parameter: `current_user_email`
  - Cannot delete treatments that have been applied

### Report Endpoints

- **GET /reports/doctors-patients**: Get doctors-patients report
  - Query parameter: `current_user_email`
  - Access limited to general managers
  - Returns comprehensive statistics about doctors and their patients

- **GET /reports/patients/{patient_id}/treatments**: Get patient treatments report
  - Path parameter: `patient_id`
  - Query parameter: `current_user_email`
  - Doctors can only access reports for their patients
  - General managers can access all reports

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

## Docker

### Running with Docker Compose

For convenience, you can use Docker Compose:

1. Start the application:
   ```bash
   docker-compose up
   ```

2. Start in detached mode:
   ```bash
   docker-compose up -d
   ```

3. Stop the application:
   ```bash
   docker-compose down
   ```

The API will be available at http://localhost:8000. The database is persisted through a volume mapping to your local filesystem.

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