from typing import Any, Dict, List


def individual_serial(todo: Dict[str, Any]) -> Dict[str, Any]:
    """
    Serialize a single todo document from MongoDB format.
    
    Args:
        todo: MongoDB document containing todo data
        
    Returns:
        Serialized todo dictionary with string ID
    """
    return {
        "id": str(todo["_id"]),
        "name": todo.get("name", ""),
        "description": todo.get("description", ""),
        "complete": todo.get("complete", False),
        "created_at": todo.get("created_at"),
        "updated_at": todo.get("updated_at"),
    }


def list_serial(todos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Serialize a list of todo documents.
    
    Args:
        todos: List of MongoDB documents
        
    Returns:
        List of serialized todo dictionaries
    """
    return [individual_serial(todo) for todo in todos]