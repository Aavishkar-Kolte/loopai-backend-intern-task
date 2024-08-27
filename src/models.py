from sqlalchemy import Column, Integer, String, DateTime, Boolean, Time
from .database import Base

class StoreStatus(Base):
    __tablename__ = "store_status"
    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(String, index=True)
    timestamp_utc = Column(DateTime)
    status = Column(Boolean)

class BusinessHours(Base):
    __tablename__ = "store_business_hours"
    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(String, index=True)
    day_of_week = Column(Integer)
    start_time_local = Column(Time)
    end_time_local = Column(Time)

class StoreTimezone(Base):
    __tablename__ = "store_timezone"
    store_id = Column(String, primary_key=True, index=True)
    timezone_str = Column(String)