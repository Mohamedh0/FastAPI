from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from routes.route import router
from config.database import MongoDB
from config.settings import get_settings
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting up application...")
    MongoDB.connect()
    yield
    # Shutdown
    logger.info("Shutting down application...")
    MongoDB.disconnect()


# Get settings
settings = get_settings()

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    ## Todo API with MongoDB

    A complete RESTful API for managing todo items.

    ### Features:
    * **Create** new todos
    * **Read** todos with filtering and pagination
    * **Update** existing todos
    * **Delete** single or multiple todos
    * **Toggle** completion status
    * **Statistics** endpoint for insights
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint - API health check."""
    return {
        "message": "Welcome to the Todo API",
        "version": settings.app_version,
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "database": "connected"}


# Include routers
app.include_router(router)

