from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default='waiter')  # 'admin', 'waiter'
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Table(Base):
    __tablename__ = "tables"
    
    table_number = Column(Integer, primary_key=True)
    code = Column(String(3), nullable=False)
    status = Column(String(10), default='free')  # 'free' or 'occupied'
    has_extra_order = Column(Boolean, default=False)
    checkout_requested = Column(Boolean, default=False)
    checkout_method = Column(String(10))  # 'cash' or 'card'
    tip_amount = Column(Float, default=0.0)
    
    orders = relationship("Order", back_populates="table")

class MenuItem(Base):
    __tablename__ = "menu_items"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    ingredients = Column(String(500))
    price = Column(Float, nullable=False)
    category = Column(String(50), default='Food')
    active = Column(Boolean, default=True)
    
    order_items = relationship("OrderItem", back_populates="menu_item")

class Waiter(Base):
    __tablename__ = "waiters"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    active = Column(Boolean, default=True)
    
    orders = relationship("Order", back_populates="waiter")

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    table_number = Column(Integer, ForeignKey('tables.table_number'))
    waiter_id = Column(Integer, ForeignKey('waiters.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(10), default='active')  # 'active' or 'finished'
    tip_amount = Column(Float, default=0.0)
    
    table = relationship("Table", back_populates="orders")
    waiter = relationship("Waiter", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order")

class OrderItem(Base):
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('orders.id'))
    product_id = Column(Integer, ForeignKey('menu_items.id'))
    qty = Column(Integer, nullable=False)
    is_extra_item = Column(Boolean, default=False)
    is_new_extra = Column(Boolean, default=False)
    customizations = Column(String(1000))  # JSON string for ingredient modifications
    
    order = relationship("Order", back_populates="order_items")
    menu_item = relationship("MenuItem", back_populates="order_items")

# Database setup
DATABASE_URL = "sqlite:///./database.db"
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