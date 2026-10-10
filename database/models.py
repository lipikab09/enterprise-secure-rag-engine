from sqlalchemy import Column, Integer, String, DateTime, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False)  # e.g., 'intern', 'engineer', 'manager'

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    user_id = Column(Integer, nullable=False)
    user_role = Column(String, nullable=False)
    query_text = Column(Text, nullable=False)
    status = Column(String, nullable=False)  # 'SUCCESS' or 'BLOCKED'

# For simplicity and fast local setup, we'll use SQLite (local file database)
DATABASE_URL = "sqlite:///./enterprise_rag.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)