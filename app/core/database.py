from pymongo import MongoClient
from pymongo.database import Database
from redis import Redis
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class Database:
    client: MongoClient = None
    db: Database = None
    redis: Redis = None

db = Database()

async def connect_to_database():
    """Connect to MongoDB and Redis"""
    try:
        # MongoDB connection
        db.client = MongoClient(settings.MONGODB_URL)
        db.db = db.client[settings.MONGODB_DB_NAME]
        
        # Test MongoDB connection
        db.client.admin.command('ping')
        logger.info("Connected to MongoDB")
        
        # Redis connection
        db.redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)
        
        # Test Redis connection
        db.redis.ping()
        logger.info("Connected to Redis")
        
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise

async def close_database_connection():
    """Close database connections"""
    if db.client:
        db.client.close()
    if db.redis:
        db.redis.close()
    logger.info("Database connections closed")