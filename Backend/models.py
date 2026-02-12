from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String, unique=True, index=True) # Example: 'P101'
    name = Column(String)
    age = Column(Integer)
    history = Column(Text) # Past medical issues store panna

    # Relationships (Optional: Future-la use aagum)
    appointments = relationship("Appointment", back_populates="patient")

class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    specialization = Column(String) # Example: Cardiology, Dermatology
    availability = Column(Boolean, default=True) # Current-ah available-ah?

    # Relationships
    appointments = relationship("Appointment", back_populates="doctor")

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    doctor_id = Column(Integer, ForeignKey("doctors.id"))
    time_slot = Column(String) # Example: "10:30 AM"
    status = Column(String, default="Scheduled")

    # Relationships link panna
    patient = relationship("Patient", back_populates="appointments")
    doctor = relationship("Doctor", back_populates="appointments")