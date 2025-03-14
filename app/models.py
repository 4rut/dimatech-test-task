import datetime
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    full_name = Column(String, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False, default="user")

    accounts = relationship("Account", back_populates="user", cascade="all, delete")
    payments = relationship("Payment", back_populates="user", cascade="all, delete")


class Account(Base):
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True)
    balance = Column(Float, default=0)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    user = relationship("User", back_populates="accounts")


class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True)
    transaction_id = Column(String, nullable=False, unique=True)
    amount = Column(Float, nullable=False)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="payments")
    __table_args__ = (UniqueConstraint("transaction_id", name="uix_transaction_id"),)
