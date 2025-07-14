from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, index=True)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    
    # Онбординг
    onboarding_step = Column(String(50), default="start")
    is_completed = Column(Boolean, default=False)
    
    # Параметры тела
    gender = Column(String(10), nullable=True)
    age = Column(Integer, nullable=True)
    height = Column(Float, nullable=True)  # см
    weight = Column(Float, nullable=True)  # кг
    chest = Column(Float, nullable=True)   # см
    waist = Column(Float, nullable=True)   # см
    hips = Column(Float, nullable=True)    # см
    foot_size = Column(Float, nullable=True)  # см
    head_circumference = Column(Float, nullable=True)  # см
    bra_size = Column(String(10), nullable=True)
    
    # TON Wallet
    ton_wallet_address = Column(String(255), nullable=True)
    
    # Токены и награды
    msz_balance = Column(Integer, default=0)
    total_earned_msz = Column(Integer, default=0)
    
    # Реферальная программа
    referral_code = Column(String(50), unique=True, nullable=True)
    referred_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    referral_count_l1 = Column(Integer, default=0)
    
    # Система
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    photos = relationship("UserPhoto", back_populates="user")
    tasks = relationship("UserTask", back_populates="user")
    referrals = relationship("User", backref="referrer", remote_side=[id])

class UserPhoto(Base):
    __tablename__ = "user_photos"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    file_id = Column(String(255))  # Telegram file_id
    file_path = Column(String(500), nullable=True)
    photo_type = Column(String(20))  # 'front', 'side', 'full'
    
    # AI валидация
    is_validated = Column(Boolean, default=False)
    validation_score = Column(Float, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="photos")

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True)
    description = Column(Text)
    reward_msz = Column(Integer)
    task_type = Column(String(50))  # 'onboarding', 'social', 'referral'
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

class UserTask(Base):
    __tablename__ = "user_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    task_id = Column(Integer, ForeignKey("tasks.id"))
    
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)
    reward_given = Column(Integer, default=0)
    
    user = relationship("User", back_populates="tasks")
    task = relationship("Task")

class SizeRecommendation(Base):
    __tablename__ = "size_recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    brand_name = Column(String(100))
    clothing_type = Column(String(100))
    recommended_size = Column(String(20))
    confidence_score = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)
