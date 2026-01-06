from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import ConnectionFailure
from config.settings import get_settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MongoDB:
    """MongoDB connection manager."""
    
    client: MongoClient = None
    db: Database = None
    
    @classmethod
    def connect(cls) -> None:
        """Establish connection to MongoDB."""
        settings = get_settings()
        try:
            cls.client = MongoClient(settings.mongodb_url)
            # Verify connection
            cls.client.admin.command('ping')
            cls.db = cls.client[settings.database_name]
            logger.info(f"Successfully connected to MongoDB: {settings.database_name}")
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    @classmethod
    def disconnect(cls) -> None:
        """Close MongoDB connection."""
        if cls.client:
            cls.client.close()
            logger.info("MongoDB connection closed")
    
    @classmethod
    def get_collection(cls, collection_name: str = None) -> Collection:
        """Get a collection from the database."""
        if cls.db is None:
            cls.connect()
        settings = get_settings()
        name = collection_name or settings.collection_name
        return cls.db[name]


def get_todo_collection() -> Collection:
    """Get the todo collection."""
    return MongoDB.get_collection()


# For backward compatibility
collection_name = None  # Will be initialized on first use

def get_collection_name() -> Collection:
    """Legacy function - returns todo collection."""
    return get_todo_collection()