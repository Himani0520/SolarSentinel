import os
import json
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

Base = declarative_base()

class Plant(Base):
    __tablename__ = 'plants'
    plant_id = Column(Integer, primary_key=True, autoincrement=True)
    plant_name = Column(String, unique=True, nullable=False)
    dataset_source = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    inverters = relationship("Inverter", back_populates="plant")

class Inverter(Base):
    __tablename__ = 'inverters'
    inverter_id = Column(String, primary_key=True)
    plant_id = Column(Integer, ForeignKey('plants.plant_id'))
    location = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    plant = relationship("Plant", back_populates="inverters")

class Telemetry(Base):
    __tablename__ = 'telemetry'
    id = Column(Integer, primary_key=True, autoincrement=True)
    plant_id = Column(Integer, ForeignKey('plants.plant_id'))
    inverter_id = Column(String, ForeignKey('inverters.inverter_id'))
    timestamp = Column(DateTime, nullable=False)

    inverter_power_mean = Column(Float)
    power_change = Column(Float)
    pv_power_total = Column(Float)
    pv_voltage_mean = Column(Float)
    pv_current_mean = Column(Float)
    
    inv_temp_mean = Column(Float)
    inv_temp_max = Column(Float)
    thermal_stress = Column(Float)
    
    freq_mean = Column(Float)
    pf_mean = Column(Float)
    
    # Store the entire row for XGBoost which requires many features
    raw_data_json = Column(Text, nullable=False)

class Prediction(Base):
    __tablename__ = 'predictions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    plant_id = Column(Integer, ForeignKey('plants.plant_id'))
    inverter_id = Column(String, ForeignKey('inverters.inverter_id'))
    timestamp = Column(DateTime, nullable=False)
    
    failure_probability = Column(Float)
    risk_level = Column(String)
    model_version = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Optional: store full multi-horizon results as JSON
    horizons_json = Column(Text)

class AiReport(Base):
    __tablename__ = 'ai_reports'
    id = Column(Integer, primary_key=True, autoincrement=True)
    plant_id = Column(Integer, ForeignKey('plants.plant_id'))
    inverter_id = Column(String, ForeignKey('inverters.inverter_id'))
    prediction_id = Column(Integer, ForeignKey('predictions.id'))
    
    report_text = Column(Text, nullable=False)
    generated_at = Column(DateTime, default=datetime.utcnow)

# Database Setup
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'solar_monitoring.db'))
engine = create_engine(f"sqlite:///{DB_PATH}")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
