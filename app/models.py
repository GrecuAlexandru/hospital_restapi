from sqlalchemy import Boolean, Column, Integer, String, Enum, ForeignKey
from sqlalchemy.orm import relationship
import enum

from .database import Base


class Role(str, enum.Enum):
    GENERAL_MANAGER = "general_manager"
    DOCTOR = "doctor"
    ASSISTANT = "assistant"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    role = Column(String)
    is_active = Column(Boolean, default=True)

    doctor = relationship("Doctor", back_populates="user", uselist=False)


class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    specialization = Column(String)
    experience = Column(Integer)

    # Relationships
    user = relationship("User", back_populates="doctor")
    patients = relationship("Patient", back_populates="doctor")
    treatments = relationship("Treatment", back_populates="doctor")


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    age = Column(Integer)
    is_active = Column(Boolean, default=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"))

    # Relationships
    doctor = relationship("Doctor", back_populates="patients")
    treatments = relationship("Treatment", back_populates="patient")


class Assistant(Base):
    __tablename__ = "assistants"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    age = Column(Integer)
    specialization = Column(String)

    # Relationships
    user = relationship("User", backref="assistant", uselist=False)
    patient_assignments = relationship("PatientAssistant", back_populates="assistant")
    treatment_applications = relationship(
        "TreatmentApplication", back_populates="assistant"
    )


class PatientAssistant(Base):
    __tablename__ = "patient_assistants"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    assistant_id = Column(Integer, ForeignKey("assistants.id"))
    assigned_by_doctor_id = Column(Integer, ForeignKey("doctors.id"))
    is_active = Column(Boolean, default=True)

    # Relationships
    patient = relationship("Patient", backref="assistant_assignments")
    assistant = relationship("Assistant", back_populates="patient_assignments")
    assigned_by_doctor = relationship("Doctor")


class Treatment(Base):
    __tablename__ = "treatments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    doctor_id = Column(Integer, ForeignKey("doctors.id"))
    patient_id = Column(Integer, ForeignKey("patients.id"))
    is_active = Column(Boolean, default=True)

    # Relationships
    doctor = relationship("Doctor", back_populates="treatments")
    patient = relationship("Patient", back_populates="treatments")
    applications = relationship("TreatmentApplication", back_populates="treatment")


class TreatmentApplication(Base):
    __tablename__ = "treatment_applications"

    id = Column(Integer, primary_key=True, index=True)
    treatment_id = Column(Integer, ForeignKey("treatments.id"))
    assistant_id = Column(Integer, ForeignKey("assistants.id"))
    notes = Column(String)

    # Relationships
    treatment = relationship("Treatment", back_populates="applications")
    assistant = relationship("Assistant", back_populates="treatment_applications")
