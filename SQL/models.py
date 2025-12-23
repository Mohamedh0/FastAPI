"""
Database Models Module
======================
This module defines SQLAlchemy ORM models for the application.
"""

from sqlalchemy import Column, Integer, String, CheckConstraint
from .database import Base


class Book(Base):
    """
    Book Model
    ----------
    Represents a book in the database.
    
    Attributes:
        id (int): Primary key, auto-incremented
        title (str): Title of the book (max 200 chars)
        author (str): Author name (max 100 chars)
        description (str): Book description (max 500 chars)
        rating (int): Rating from 0 to 100
    """
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(200), nullable=False, index=True)
    author = Column(String(100), nullable=False, index=True)
    description = Column(String(500), nullable=True)
    rating = Column(Integer, nullable=False, default=0)

    # Add constraint to ensure rating is between 0 and 100
    __table_args__ = (
        CheckConstraint('rating >= 0 AND rating <= 100', name='valid_rating'),
    )

    def __repr__(self) -> str:
        return f"<Book(id={self.id}, title='{self.title}', author='{self.author}')>"