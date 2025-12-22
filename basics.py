"""
HTTP Requests
1- GET => Read Resource
2- POST => Create Resource
3- PUT => Update / Replace Resource
4- DELETE => Delete Resource
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from typing import Optional

app = FastAPI(
    title="Book API",
    description="A simple API to manage books",
    version="1.0.0"
)


# ============== Models ==============

class BookCreate(BaseModel):
    """Model for creating a new book (without ID)"""
    title: str = Field(min_length=1, max_length=200, description="The title of the book")
    author: str = Field(min_length=1, max_length=100, description="The author of the book")
    description: str = Field(min_length=1, max_length=500, description="A brief description of the book")
    rating: int = Field(ge=0, le=100, description="Rating from 0 to 100")



class BookUpdate(BaseModel):
    """Model for updating a book (all fields optional)"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    author: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, min_length=1, max_length=500)
    rating: Optional[int] = Field(None, ge=0, le=100)


class Book(BaseModel):
    """Complete book model with ID"""
    id: UUID
    title: str = Field(min_length=1, max_length=200)
    author: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1, max_length=500)
    rating: int = Field(ge=0, le=100)


class MessageResponse(BaseModel):
    """Response model for messages"""
    message: str
    detail: Optional[str] = None


# ============== In-Memory Database ==============

BOOKS: list[Book] = []


# ============== Helper Functions ==============

def find_book_by_id(book_id: UUID) -> tuple[int, Book] | None:
    """Find a book by its ID and return its index and the book object"""
    for index, book in enumerate(BOOKS):
        if book.id == book_id:
            return index, book
    return None


# ============== API Endpoints ==============

# GET - Read all books
@app.get(
    "/books",
    response_model=list[Book],
    status_code=status.HTTP_200_OK,
    summary="Get all books",
    description="Retrieve a list of all books in the database"
)
def get_all_books():
    """Get all books from the database"""
    return BOOKS


# GET - Read a single book by ID
@app.get(
    "/books/{book_id}",
    response_model=Book,
    status_code=status.HTTP_200_OK,
    summary="Get a book by ID",
    responses={
        404: {"model": MessageResponse, "description": "Book not found"}
    }
)
def get_book(book_id: UUID):
    """Get a specific book by its ID"""
    result = find_book_by_id(book_id)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {book_id} not found"
        )
    return result[1]


# POST - Create a new book
@app.post(
    "/books",
    response_model=Book,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new book",
    responses={
        400: {"model": MessageResponse, "description": "Invalid input"}
    }
)
def create_book(book_data: BookCreate):
    """Create a new book with an auto-generated UUID"""
    new_book = Book(
        id=uuid4(),
        title=book_data.title,
        author=book_data.author,
        description=book_data.description,
        rating=book_data.rating
    )
    BOOKS.append(new_book)
    return new_book


# PUT - Update/Replace a book
@app.put(
    "/books/{book_id}",
    response_model=Book,
    status_code=status.HTTP_200_OK,
    summary="Update a book",
    responses={
        404: {"model": MessageResponse, "description": "Book not found"}
    }
)
def update_book(book_id: UUID, book_data: BookUpdate):
    """Update an existing book by its ID"""
    result = find_book_by_id(book_id)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {book_id} not found"
        )
    
    index, existing_book = result
    
    # Update only the fields that were provided
    update_data = book_data.model_dump(exclude_unset=True)
    updated_book = existing_book.model_copy(update=update_data)
    
    BOOKS[index] = updated_book
    return updated_book


# DELETE - Delete a book
@app.delete(
    "/books/{book_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a book",
    responses={
        404: {"model": MessageResponse, "description": "Book not found"}
    }
)
def delete_book(book_id: UUID):
    """Delete a book by its ID"""
    result = find_book_by_id(book_id)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {book_id} not found"
        )
    
    index, deleted_book = result
    BOOKS.pop(index)
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Book deleted successfully",
            "deleted_book": {
                "id": str(deleted_book.id),
                "title": deleted_book.title
            }
        }
    )


# DELETE - Delete all books
@app.delete(
    "/books",
    status_code=status.HTTP_200_OK,
    summary="Delete all books"
)
def delete_all_books():
    """Delete all books from the database"""
    count = len(BOOKS)
    BOOKS.clear()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": f"Successfully deleted {count} book(s)"
        }
    )
