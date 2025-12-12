"""
MongoDB Database Connection and Operations
Handles all database interactions for the Career Path Simulator
"""

import os
from datetime import datetime
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from dotenv import load_dotenv

load_dotenv()

# MongoDB connection
DATABASE_URL = os.getenv("DATABASE_URL")
client: Optional[AsyncIOMotorClient] = None
db = None


async def connect_to_mongodb():
    """Initialize MongoDB connection"""
    global client, db
    try:
        client = AsyncIOMotorClient(DATABASE_URL)
        # Verify connection
        await client.admin.command('ping')
        db = client.get_default_database()
        print("✅ Connected to MongoDB successfully!")
        return True
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        return False


async def close_mongodb_connection():
    """Close MongoDB connection"""
    global client
    if client:
        client.close()
        print("👋 MongoDB connection closed")


def get_database():
    """Get database instance"""
    return db


async def save_user_profile(profile_data: dict, user_id: Optional[str] = None) -> dict:
    """
    Save user profile to MongoDB
    
    Args:
        profile_data: The career profile data from the form
        user_id: Optional user ID if authenticated
    
    Returns:
        dict with success status and inserted ID
    """
    if db is None:
        raise Exception("Database not connected")
    
    collection = db.user_profiles
    
    # Prepare document
    document = {
        **profile_data,
        "user_id": user_id,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    
    # Insert document
    result = await collection.insert_one(document)
    
    return {
        "success": True,
        "profile_id": str(result.inserted_id),
        "message": "Profile saved successfully"
    }


async def get_user_profile(profile_id: str) -> Optional[dict]:
    """
    Get user profile by ID
    
    Args:
        profile_id: The profile document ID
    
    Returns:
        The profile document or None
    """
    if db is None:
        raise Exception("Database not connected")
    
    from bson import ObjectId
    
    collection = db.user_profiles
    document = await collection.find_one({"_id": ObjectId(profile_id)})
    
    if document:
        document["_id"] = str(document["_id"])
    
    return document


async def get_user_profiles_by_user_id(user_id: str) -> list:
    """
    Get all profiles for a specific user
    
    Args:
        user_id: The user ID
    
    Returns:
        List of profile documents
    """
    if db is None:
        raise Exception("Database not connected")
    
    collection = db.user_profiles
    cursor = collection.find({"user_id": user_id}).sort("created_at", -1)
    profiles = await cursor.to_list(length=100)
    
    for profile in profiles:
        profile["_id"] = str(profile["_id"])
    
    return profiles


async def update_user_profile(profile_id: str, profile_data: dict) -> dict:
    """
    Update an existing user profile
    
    Args:
        profile_id: The profile document ID
        profile_data: The updated profile data
    
    Returns:
        dict with success status
    """
    if db is None:
        raise Exception("Database not connected")
    
    from bson import ObjectId
    
    collection = db.user_profiles
    
    # Update document
    result = await collection.update_one(
        {"_id": ObjectId(profile_id)},
        {
            "$set": {
                **profile_data,
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    return {
        "success": result.modified_count > 0,
        "message": "Profile updated successfully" if result.modified_count > 0 else "No changes made"
    }


async def delete_user_profile(profile_id: str) -> dict:
    """
    Delete a user profile
    
    Args:
        profile_id: The profile document ID
    
    Returns:
        dict with success status
    """
    if db is None:
        raise Exception("Database not connected")
    
    from bson import ObjectId
    
    collection = db.user_profiles
    result = await collection.delete_one({"_id": ObjectId(profile_id)})
    
    return {
        "success": result.deleted_count > 0,
        "message": "Profile deleted successfully" if result.deleted_count > 0 else "Profile not found"
    }
