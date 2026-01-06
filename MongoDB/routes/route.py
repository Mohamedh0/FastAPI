from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Optional
from models.todos import TodoCreate, TodoUpdate, TodoResponse
from config.database import get_todo_collection
from schema.schemas import list_serial, individual_serial
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime

router = APIRouter(prefix="/todos", tags=["Todos"])


def validate_object_id(id: str) -> ObjectId:
    """Validate and convert string to ObjectId."""
    try:
        return ObjectId(id)
    except InvalidId:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid ID format: {id}"
        )


@router.get("/", response_model=List[TodoResponse], summary="Get all todos")
async def get_todos(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    complete: Optional[bool] = Query(None, description="Filter by completion status")
):
    """
    Retrieve all todos with optional filtering and pagination.
    
    - **skip**: Number of records to skip (for pagination)
    - **limit**: Maximum number of records to return
    - **complete**: Filter by completion status (optional)
    """
    collection = get_todo_collection()
    
    # Build query filter
    query = {}
    if complete is not None:
        query["complete"] = complete
    
    todos = collection.find(query).skip(skip).limit(limit)
    return list_serial(todos)


@router.get("/{id}", response_model=TodoResponse, summary="Get a todo by ID")
async def get_todo(id: str):
    """
    Retrieve a specific todo by its ID.
    
    - **id**: The unique identifier of the todo
    """
    collection = get_todo_collection()
    object_id = validate_object_id(id)
    
    todo = collection.find_one({"_id": object_id})
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo with ID {id} not found"
        )
    
    return individual_serial(todo)


@router.post("/", response_model=TodoResponse, status_code=status.HTTP_201_CREATED, summary="Create a new todo")
async def create_todo(todo: TodoCreate):
    """
    Create a new todo item.
    
    - **name**: Todo name (required)
    - **description**: Todo description (required)
    - **complete**: Completion status (default: false)
    """
    collection = get_todo_collection()
    
    # Prepare document with timestamps
    todo_dict = todo.model_dump()
    todo_dict["created_at"] = datetime.utcnow()
    todo_dict["updated_at"] = datetime.utcnow()
    
    result = collection.insert_one(todo_dict)
    
    # Fetch and return the created todo
    created_todo = collection.find_one({"_id": result.inserted_id})
    return individual_serial(created_todo)


@router.put("/{id}", response_model=TodoResponse, summary="Update a todo")
async def update_todo(id: str, todo: TodoUpdate):
    """
    Update an existing todo item.
    
    - **id**: The unique identifier of the todo
    - **name**: New todo name (optional)
    - **description**: New todo description (optional)
    - **complete**: New completion status (optional)
    """
    collection = get_todo_collection()
    object_id = validate_object_id(id)
    
    # Check if todo exists
    existing_todo = collection.find_one({"_id": object_id})
    if not existing_todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo with ID {id} not found"
        )
    
    # Build update data (only non-None fields)
    update_data = {k: v for k, v in todo.model_dump().items() if v is not None}
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid fields to update"
        )
    
    update_data["updated_at"] = datetime.utcnow()
    
    collection.update_one({"_id": object_id}, {"$set": update_data})
    
    # Fetch and return the updated todo
    updated_todo = collection.find_one({"_id": object_id})
    return individual_serial(updated_todo)


@router.patch("/{id}/toggle", response_model=TodoResponse, summary="Toggle todo completion")
async def toggle_todo(id: str):
    """
    Toggle the completion status of a todo.
    
    - **id**: The unique identifier of the todo
    """
    collection = get_todo_collection()
    object_id = validate_object_id(id)
    
    # Check if todo exists
    todo = collection.find_one({"_id": object_id})
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo with ID {id} not found"
        )
    
    # Toggle completion status
    new_status = not todo.get("complete", False)
    collection.update_one(
        {"_id": object_id},
        {"$set": {"complete": new_status, "updated_at": datetime.utcnow()}}
    )
    
    updated_todo = collection.find_one({"_id": object_id})
    return individual_serial(updated_todo)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a todo")
async def delete_todo(id: str):
    """
    Delete a todo item.
    
    - **id**: The unique identifier of the todo to delete
    """
    collection = get_todo_collection()
    object_id = validate_object_id(id)
    
    result = collection.delete_one({"_id": object_id})
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo with ID {id} not found"
        )
    
    return None


@router.delete("/completed/all", status_code=status.HTTP_200_OK, summary="Delete all completed todos")
async def delete_completed_todos():
    """
    Delete all todos that are marked as complete.
    
    Returns the count of deleted todos.
    """
    collection = get_todo_collection()
    
    result = collection.delete_many({"complete": True})
    
    return {"message": f"Deleted {result.deleted_count} completed todos"}


@router.get("/stats/summary", summary="Get todo statistics")
async def get_todo_stats():
    """
    Get statistics about todos.
    
    Returns total count, completed count, and pending count.
    """
    collection = get_todo_collection()
    
    total = collection.count_documents({})
    completed = collection.count_documents({"complete": True})
    pending = total - completed
    
    return {
        "total": total,
        "completed": completed,
        "pending": pending,
        "completion_rate": round((completed / total * 100), 2) if total > 0 else 0
    }