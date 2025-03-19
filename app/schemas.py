from pydantic import BaseModel, EmailStr
from typing import Optional, List


# User schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True


# Doctor schemas
class DoctorBase(BaseModel):
    specialization: Optional[str] = None
    experience: Optional[int] = None


class DoctorCreate(DoctorBase):
    email: EmailStr
    full_name: str
    password: str
    specialization: str
    experience: int


class DoctorUpdate(BaseModel):
    is_active: Optional[bool] = None
    specialization: Optional[str] = None
    experience: Optional[int] = None


class Doctor(DoctorBase):
    id: int
    user_id: int
    specialization: str
    experience: int

    # Include user information
    user: User

    class Config:
        from_attributes = True


class DoctorList(DoctorBase):
    id: int
    user_id: int
    user: User

    class Config:
        from_attributes = True


# Patient schemas
class PatientBase(BaseModel):
    first_name: str
    last_name: str
    age: Optional[int] = None


class PatientCreate(PatientBase):
    pass


class PatientUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    age: Optional[int] = None


class Patient(PatientBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True


# Assistant schemas
class AssistantBase(BaseModel):
    age: Optional[int] = None
    specialization: Optional[str] = None


class AssistantCreate(AssistantBase):
    email: EmailStr
    full_name: str
    password: str
    age: int
    specialization: str


class AssistantUpdate(BaseModel):
    is_active: Optional[bool] = None
    age: Optional[int] = None
    specialization: Optional[str] = None


class Assistant(AssistantBase):
    id: int
    user_id: int
    age: int
    specialization: str

    # Include user information
    user: User

    class Config:
        from_attributes = True


class AssistantList(AssistantBase):
    id: int
    user_id: int
    user: User

    class Config:
        from_attributes = True


# Patient - Assistant Assignment schemas
class PatientAssistantBase(BaseModel):
    patient_id: int
    assistant_id: int


class PatientAssistantCreate(PatientAssistantBase):
    pass


class PatientAssistantUpdate(BaseModel):
    is_active: Optional[bool] = None


class PatientAssistant(PatientAssistantBase):
    id: int
    assigned_by_doctor_id: int
    is_active: bool

    class Config:
        from_attributes = True


# Treatment schemas
class TreatmentBase(BaseModel):
    name: str
    description: Optional[str] = None
    patient_id: int


class TreatmentCreate(TreatmentBase):
    pass


class TreatmentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class Treatment(TreatmentBase):
    id: int
    doctor_id: int
    is_active: bool

    class Config:
        from_attributes = True


# TreatmentApplication schemas
class TreatmentApplicationBase(BaseModel):
    treatment_id: int
    notes: Optional[str] = None
    application_date: str


class TreatmentApplicationCreate(TreatmentApplicationBase):
    pass


class TreatmentApplicationUpdate(BaseModel):
    notes: Optional[str] = None


class TreatmentApplication(TreatmentApplicationBase):
    id: int
    assistant_id: int

    class Config:
        from_attributes = True


# Treatment Report schemas
class TreatmentReport(BaseModel):
    treatment: Treatment
    applications: List[TreatmentApplication] = []

    class Config:
        from_attributes = True
