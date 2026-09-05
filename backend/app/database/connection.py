import logging
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import IndexModel, ASCENDING, DESCENDING
from app.config import settings

logger = logging.getLogger("sif_backend")


class DatabaseManager:
    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None


db_manager = DatabaseManager()


def _sanitize_uri(uri: str) -> str:
    import re
    return re.sub(r'mongodb(\+srv)?://([^:]+):([^@]+)@', r'mongodb\1://\2:****@', uri)


async def connect_to_mongo():
    sanitized_uri = _sanitize_uri(settings.MONGODB_URI)
    logger.info(f"Connecting to MongoDB at {sanitized_uri} ...")
    try:
        db_manager.client = AsyncIOMotorClient(
            settings.MONGODB_URI,
            serverSelectionTimeoutMS=5000
        )
        # Test connection ping
        await db_manager.client.admin.command('ping')
        db_manager.db = db_manager.client[settings.DATABASE_NAME]
        logger.info(f"Connected to MongoDB database: {settings.DATABASE_NAME}")

        await create_indexes()
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB ({sanitized_uri}): {str(e)}")
        # We allow client initialization so startup doesn't fail hard if DB is down initially,
        # but mark db as unready or let endpoints return 503 if disconnected.


async def close_mongo_connection():
    if db_manager.client:
        logger.info("Closing MongoDB connection ...")
        db_manager.client.close()
        logger.info("MongoDB connection closed.")


def get_database() -> AsyncIOMotorDatabase:
    if db_manager.db is None:
        raise RuntimeError("Database connection not initialized")
    return db_manager.db


async def create_indexes():
    if db_manager.db is None:
        return

    try:
        # Users indexes
        users_col = db_manager.db["users"]
        await users_col.create_index([("email", ASCENDING)], unique=True)
        await users_col.create_index([("username", ASCENDING)], unique=True)

        # Reports indexes
        reports_col = db_manager.db["reports"]
        await reports_col.create_index([("report_id", ASCENDING)], unique=True)
        await reports_col.create_index([("created_at", DESCENDING)])
        await reports_col.create_index([("status", ASCENDING)])
        await reports_col.create_index([("report_type", ASCENDING)])
        await reports_col.create_index([("department", ASCENDING)])
        await reports_col.create_index([("location", ASCENDING)])
        await reports_col.create_index([("analysis.sif_precursor", ASCENDING)])
        await reports_col.create_index([("risk.level", ASCENDING)])

        # Rules indexes
        rules_col = db_manager.db["rules"]
        await rules_col.create_index([("rule_id", ASCENDING)], unique=True)

        # Actions indexes
        actions_col = db_manager.db["actions"]
        await actions_col.create_index([("action_id", ASCENDING)], unique=True)
        await actions_col.create_index([("report_id", ASCENDING)])
        await actions_col.create_index([("assigned_to", ASCENDING)])
        await actions_col.create_index([("status", ASCENDING)])

        logger.info("MongoDB indexes created successfully.")
    except Exception as e:
        logger.warning(f"Error creating MongoDB indexes: {str(e)}")
