from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime

Base = declarative_base()

class Agency(Base):
    __tablename__ = "agencies"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    subdomain = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    phone = Column(String(20))
    email = Column(String(255))
    address = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    active = Column(Boolean, default=True)
    
    # Relationships
    users = relationship("User", back_populates="agency")
    models = relationship("Model", back_populates="agency")
    cities = relationship("City", back_populates="agency")
    bookings = relationship("Booking", back_populates="agency")

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    agency_id = Column(Integer, ForeignKey('agencies.id'), nullable=False)
    username = Column(String(50), nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default='admin')  # 'admin', 'staff'
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    agency = relationship("Agency", back_populates="users")
    
    __table_args__ = (
        {'sqlite_autoincrement': True}
    )

class City(Base):
    __tablename__ = "cities"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    agency_id = Column(Integer, ForeignKey('agencies.id'), nullable=False)
    name = Column(String(100), nullable=False)
    country = Column(String(50), default='Spain')
    active = Column(Boolean, default=True)
    
    agency = relationship("Agency", back_populates="cities")
    models = relationship("Model", back_populates="city")

class Model(Base):
    __tablename__ = "models"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    agency_id = Column(Integer, ForeignKey('agencies.id'), nullable=False)
    city_id = Column(Integer, ForeignKey('cities.id'), nullable=True)
    name = Column(String(100), nullable=False)
    age = Column(Integer)
    height = Column(Integer)  # in cm
    hair_color = Column(String(50))
    eye_color = Column(String(50))
    bio = Column(Text)
    photos = Column(Text)  # JSON array of photo URLs
    status = Column(String(20), default='pending')  # pending, approved, rejected
    available = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    agency = relationship("Agency", back_populates="models")
    city = relationship("City", back_populates="models")
    bookings = relationship("Booking", back_populates="model")

class Booking(Base):
    __tablename__ = "bookings"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    agency_id = Column(Integer, ForeignKey('agencies.id'), nullable=False)
    model_id = Column(Integer, ForeignKey('models.id'), nullable=False)
    client_name = Column(String(100), nullable=False)
    client_email = Column(String(255), nullable=False)
    client_phone = Column(String(20))
    event_date = Column(DateTime)
    event_type = Column(String(100))
    message = Column(Text)
    status = Column(String(20), default='pending')  # pending, confirmed, cancelled
    created_at = Column(DateTime, default=datetime.utcnow)
    
    agency = relationship("Agency", back_populates="bookings")
    model = relationship("Model", back_populates="bookings")

# Legacy tables for compatibility (can be removed later)
class Table(Base):
    __tablename__ = "tables"
    id = Column(Integer, primary_key=True)
    
class MenuItem(Base):
    __tablename__ = "menu_items"
    id = Column(Integer, primary_key=True)
    
class Waiter(Base):
    __tablename__ = "waiters"
    id = Column(Integer, primary_key=True)
    
class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)

class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True)

class AnalyticsRecord(Base):
    __tablename__ = "analytics_records"
    id = Column(Integer, primary_key=True)

# Database setup
import os
from dotenv import load_dotenv

# Load environment variables from .env.local if it exists
if os.path.exists('.env.local'):
    load_dotenv('.env.local')

# Use SQLite for development
DATABASE_URL = "sqlite:///./agency.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()