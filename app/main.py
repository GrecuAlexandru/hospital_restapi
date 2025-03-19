from fastapi import FastAPI, Depends, HTTPException, status, Form
from sqlalchemy.orm import Session
import sys

from . import schemas, crud
from .database import engine, Base, SessionLocal
from .dependencies import get_db
from .auth_utils import (
    authenticate_user,
    get_current_user_by_email,
    check_general_manager,
)
from .routers import doctors, patients, assistants, treatment, reports
from .fixtures import create_initial_fixtures

# Create tables
Base.metadata.create_all(bind=engine)

# Check for --with-fixtures command line argument
if "--with-fixtures" in sys.argv:
    with SessionLocal() as db:
        create_initial_fixtures(db)

app = FastAPI()

# Include routers
app.include_router(doctors.router)
app.include_router(patients.router)
app.include_router(assistants.router)
app.include_router(treatment.router)
app.include_router(reports.router)


@app.post("/login")
def login(
    email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)
):
    user = authenticate_user(db, email, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}


# Protected endpoints
@app.get("/me")
def read_own_data(email: str, db: Session = Depends(get_db)):
    user = get_current_user_by_email(db, email)
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
    }


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.users.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.users.create_user(db=db, user=user)


@app.get("/users/", response_model=list[schemas.User])
def read_users(
    skip: int = 0,
    limit: int = 100,
    current_user_email: str = None,
    db: Session = Depends(get_db),
):
    # If current_user_email is provided, check permissions
    if current_user_email:
        current_user = get_current_user_by_email(db, current_user_email)
        # Only general managers can get all users
        check_general_manager(current_user)

    users = crud.users.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(
    user_id: int, current_user_email: str = None, db: Session = Depends(get_db)
):
    # If current_user_email is provided, check permissions
    if current_user_email:
        current_user = get_current_user_by_email(db, current_user_email)
        # General managers can access any user, others can only access themselves
        if current_user.role != "general_manager" and current_user.id != user_id:
            raise HTTPException(
                status_code=403, detail="Not authorized to access this user"
            )

    db_user = crud.users.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user
