"""
Book API - Main Application
===========================
A RESTful API to manage books using FastAPI and SQLAlchemy.

HTTP Methods:
    - GET    : Read resources
    - POST   : Create resources
    - PUT    : Update/Replace resources
    - DELETE : Delete resources
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List

from .database import engine, get_db, Base
from .models import Book
from .schemas import BookCreate, BookUpdate, BookResponse, MessageResponse, DeleteResponse

# ============== Create Database Tables ==============
Base.metadata.create_all(bind=engine)


# ============== FastAPI Application ==============
app = FastAPI(
    title="Book API",
    description="""
    A simple RESTful API to manage books.
    
    ## Features
    - Create, Read, Update, and Delete books
    - SQLite database for persistence
    - Input validation with Pydantic
    """,
    version="1.0.0",
    contact={
        "name": "API Support",
    },
)


# ============== API Endpoints ==============

@app.get(
    "/",
    summary="Root endpoint",
    tags=["General"]
)
def root():
    """Welcome message and API info"""
    return {
        "message": "Welcome to the Book API",
        "docs": "/docs",
        "version": "1.0.0"
    }


@app.get(
    "/books",
    response_model=List[BookResponse],
    status_code=status.HTTP_200_OK,
    summary="Get all books",
    description="Retrieve a list of all books in the database",
    tags=["Books"]
)
def get_all_books(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all books with optional pagination.
    
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to return (default: 100)
    """
    books = db.query(Book).offset(skip).limit(limit).all()
    return books


@app.get(
    "/books/{book_id}",
    response_model=BookResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a book by ID",
    responses={
        404: {"model": MessageResponse, "description": "Book not found"}
    },
    tags=["Books"]
)
def get_book(book_id: int, db: Session = Depends(get_db)):
    """Get a specific book by its ID"""
    book = db.query(Book).filter(Book.id == book_id).first()
    
    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {book_id} not found"
        )
    return book


@app.get(
    "/books/search/",
    response_model=List[BookResponse],
    summary="Search books",
    tags=["Books"]
)
def search_books(
    title: str = None,
    author: str = None,
    min_rating: int = None,
    db: Session = Depends(get_db)
):
    """
    Search books by title, author, or minimum rating.
    
    - **title**: Filter by title (partial match)
    - **author**: Filter by author (partial match)
    - **min_rating**: Filter by minimum rating
    """
    query = db.query(Book)
    
    if title:
        query = query.filter(Book.title.ilike(f"%{title}%"))
    if author:
        query = query.filter(Book.author.ilike(f"%{author}%"))
    if min_rating is not None:
        query = query.filter(Book.rating >= min_rating)
    
    return query.all()


@app.post(
    "/books",
    response_model=BookResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new book",
    tags=["Books"]
)
def create_book(book_data: BookCreate, db: Session = Depends(get_db)):
    """Create a new book in the database"""
    new_book = Book(
        title=book_data.title,
        author=book_data.author,
        description=book_data.description,
        rating=book_data.rating
    )
    
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    
    return new_book


@app.put(
    "/books/{book_id}",
    response_model=BookResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a book",
    responses={
        404: {"model": MessageResponse, "description": "Book not found"}
    },
    tags=["Books"]
)
def update_book(book_id: int, book_data: BookUpdate, db: Session = Depends(get_db)):
    """Update an existing book by its ID (partial update supported)"""
    book = db.query(Book).filter(Book.id == book_id).first()
    
    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {book_id} not found"
        )
    
    # Update only provided fields
    update_data = book_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(book, field, value)
    
    db.commit()
    db.refresh(book)
    
    return book


@app.delete(
    "/books/{book_id}",
    response_model=DeleteResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete a book",
    responses={
        404: {"model": MessageResponse, "description": "Book not found"}
    },
    tags=["Books"]
)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    """Delete a book by its ID"""
    book = db.query(Book).filter(Book.id == book_id).first()
    
    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {book_id} not found"
        )
    
    deleted_title = book.title
    db.delete(book)
    db.commit()
    
    return DeleteResponse(
        message="Book deleted successfully",
        deleted_id=book_id,
        deleted_title=deleted_title
    )


@app.delete(
    "/books",
    status_code=status.HTTP_200_OK,
    summary="Delete all books",
    tags=["Books"]
)
def delete_all_books(db: Session = Depends(get_db)):
    """Delete all books from the database"""
    count = db.query(Book).count()
    db.query(Book).delete()
    db.commit()
    
    return {"message": f"Successfully deleted {count} book(s)"}
