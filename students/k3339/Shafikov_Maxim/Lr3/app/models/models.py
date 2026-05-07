from datetime import date, datetime
from enum import Enum
from typing import List, Optional

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(AsyncAttrs, DeclarativeBase):
    pass


class TransactionType(str, Enum):
    income = "income"
    expense = "expense"


class PeriodType(str, Enum):
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"
    yearly = "yearly"


class TransactionTag(Base):
    __tablename__ = "transaction_tag"

    transaction_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("transaction.id", ondelete="CASCADE"), primary_key=True
    )
    tag_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("tag.id", ondelete="CASCADE"), primary_key=True
    )
    added_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    transactions: Mapped[List["Transaction"]] = relationship(
        "Transaction", back_populates="user", lazy="selectin", cascade="all, delete"
    )
    budgets: Mapped[List["Budget"]] = relationship(
        "Budget", back_populates="user", lazy="selectin", cascade="all, delete"
    )
    goals: Mapped[List["Goal"]] = relationship(
        "Goal", back_populates="user", lazy="selectin", cascade="all, delete"
    )


class Category(Base):
    __tablename__ = "category"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[TransactionType] = mapped_column(String(50), nullable=False)

    transactions: Mapped[List["Transaction"]] = relationship(
        "Transaction", back_populates="category", lazy="selectin"
    )
    budgets: Mapped[List["Budget"]] = relationship(
        "Budget", back_populates="category", lazy="selectin"
    )


class Tag(Base):
    __tablename__ = "tag"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)

    transactions: Mapped[List["Transaction"]] = relationship(
        "Transaction", back_populates="tags", secondary="transaction_tag", lazy="selectin"
    )


class Transaction(Base):
    __tablename__ = "transaction"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("category.id"), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="transactions", lazy="selectin")
    category: Mapped["Category"] = relationship(
        "Category", back_populates="transactions", lazy="selectin"
    )
    tags: Mapped[List["Tag"]] = relationship(
        "Tag", back_populates="transactions", secondary="transaction_tag", lazy="selectin"
    )


class Budget(Base):
    __tablename__ = "budget"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    limit_amount: Mapped[float] = mapped_column(Float, nullable=False)
    period: Mapped[PeriodType] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("category.id"), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="budgets", lazy="selectin")
    category: Mapped["Category"] = relationship(
        "Category", back_populates="budgets", lazy="selectin"
    )


class Goal(Base):
    __tablename__ = "goal"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    target_amount: Mapped[float] = mapped_column(Float, nullable=False)
    current_amount: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    deadline: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )

    user: Mapped["User"] = relationship("User", back_populates="goals", lazy="selectin")


class ParsedPage(Base):
    """Stores parsed web page titles (from lab 2 parser, integrated in lab 3)."""
    __tablename__ = "parsed_page"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    parsed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
