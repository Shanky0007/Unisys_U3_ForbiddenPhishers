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
    Save or update user profile to MongoDB (upsert)
    If a profile already exists for the user_id, it will be updated.
    If no profile exists, a new one will be created.
    
    Args:
        profile_data: The career profile data from the form
        user_id: Optional user ID if authenticated
    
    Returns:
        dict with success status and profile ID
    """
    if db is None:
        raise Exception("Database not connected")
    
    collection = db.user_profiles
    
    # Check if profile already exists for this user
    if user_id:
        existing_profile = await collection.find_one({"user_id": user_id})
        
        if existing_profile:
            # Update existing profile
            update_data = {
                **profile_data,
                "user_id": user_id,
                "updated_at": datetime.utcnow(),
            }
            # Remove created_at from update to preserve original creation time
            update_data.pop("created_at", None)
            
            await collection.update_one(
                {"user_id": user_id},
                {"$set": update_data}
            )
            
            return {
                "success": True,
                "profile_id": str(existing_profile["_id"]),
                "message": "Profile updated successfully",
                "is_new": False
            }
    
    # Create new profile (no user_id or no existing profile)
    document = {
        **profile_data,
        "user_id": user_id,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    
    result = await collection.insert_one(document)
    
    return {
        "success": True,
        "profile_id": str(result.inserted_id),
        "message": "Profile created successfully",
        "is_new": True
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


async def get_user_by_id(user_id: str) -> Optional[dict]:
    """
    Get user by user_id from the users collection
    
    Args:
        user_id: The user ID (string format of ObjectId)
    
    Returns:
        The user document or None if not found
    """
    if db is None:
        raise Exception("Database not connected")
    
    from bson import ObjectId
    
    # List all collections to find the users collection
    collections = await db.list_collection_names()
    
    document = None
    for collection_name in ['users', 'User', 'user']:
        if collection_name in collections:
            collection = db[collection_name]
            try:
                # Try to find by ObjectId first
                document = await collection.find_one({"_id": ObjectId(user_id)})
                if document:
                    document["_id"] = str(document["_id"])
                    print(f"✅ Found user by ID in {collection_name}")
                    return document
            except Exception as e:
                print(f"⚠️ Error searching by ObjectId: {e}")
                # Try with string ID if ObjectId fails
                document = await collection.find_one({"_id": user_id})
                if document:
                    document["_id"] = str(document["_id"])
                    print(f"✅ Found user by string ID in {collection_name}")
                    return document
    
    print(f"❌ No user found for ID: {user_id}")
    return None


async def get_user_by_phone(phone_number: str) -> Optional[dict]:
    """
    Get user by phone number from the users collection
    
    Args:
        phone_number: The phone number to search for (e.g., '+918081239465')
    
    Returns:
        The user document or None if not found
    """
    if db is None:
        raise Exception("Database not connected")
    
    # Try different phone number formats
    # Remove any spaces or dashes
    clean_phone = phone_number.replace(" ", "").replace("-", "")
    
    print(f"🔍 Searching for phone: {clean_phone}")
    
    # List all collections to debug
    collections = await db.list_collection_names()
    print(f"📂 Available collections: {collections}")
    
    # Try 'users' collection first (common naming)
    document = None
    for collection_name in ['users', 'User', 'user']:
        if collection_name in collections:
            collection = db[collection_name]
            print(f"🔎 Trying collection: {collection_name}")
            
            # Search with exact match first
            document = await collection.find_one({"phone": clean_phone})
            if document:
                print(f"✅ Found with exact match in {collection_name}")
                break
            
            # If not found, try without the '+' prefix
            if clean_phone.startswith("+"):
                document = await collection.find_one({"phone": clean_phone[1:]})
                if document:
                    print(f"✅ Found without + prefix in {collection_name}")
                    break
            
            # If not found, try with '+' prefix
            if not clean_phone.startswith("+"):
                document = await collection.find_one({"phone": f"+{clean_phone}"})
                if document:
                    print(f"✅ Found with + prefix in {collection_name}")
                    break
    
    if not document:
        print(f"❌ No user found for phone: {clean_phone}")
    
    if document:
        document["_id"] = str(document["_id"])
    
    return document


async def get_user_profile_by_user_id(user_id: str) -> Optional[dict]:
    """
    Get the most recent user profile by user_id
    
    Args:
        user_id: The user ID (string format of ObjectId)
    
    Returns:
        The profile document or None if not found
    """
    if db is None:
        raise Exception("Database not connected")
    
    collection = db.user_profiles
    
    # Get the most recent profile for this user
    document = await collection.find_one(
        {"user_id": user_id},
        sort=[("created_at", -1)]
    )
    
    if document:
        document["_id"] = str(document["_id"])
    
    return document


async def save_career_roadmap(roadmap_data: dict, user_id: str) -> dict:
    """
    Save or update career roadmap to MongoDB (upsert).
    Each user can only have ONE active career roadmap.
    If a roadmap already exists for the user, it will be replaced.
    
    Args:
        roadmap_data: The complete roadmap/dashboard data including:
            - selected_career: The career chosen by user
            - dashboard_data: All visualization data
            - timeline: Career timeline
            - financial_analysis: ROI and cost analysis
            - risk_assessment: Success probability and risks
            - gap_analysis: Skills and education gaps
        user_id: The user's ID
    
    Returns:
        dict with success status and roadmap ID
    """
    if db is None:
        raise Exception("Database not connected")
    
    if not user_id:
        raise ValueError("user_id is required to save career roadmap")
    
    collection = db.career_roadmaps
    
    # Check if a roadmap already exists for this user
    existing_roadmap = await collection.find_one({"user_id": user_id})
    
    # Prepare document
    document = {
        "user_id": user_id,
        "selected_career": roadmap_data.get("selected_career"),
        "dashboard_data": roadmap_data.get("dashboard_data"),
        "timeline": roadmap_data.get("timeline"),
        "financial_analysis": roadmap_data.get("financial_analysis"),
        "risk_assessment": roadmap_data.get("risk_assessment"),
        "gap_analysis": roadmap_data.get("gap_analysis"),
        "summary": roadmap_data.get("summary"),
        "updated_at": datetime.utcnow(),
    }
    
    if existing_roadmap:
        # Delete existing roadmap and create new one (replace)
        await collection.delete_one({"user_id": user_id})
        document["created_at"] = datetime.utcnow()
        result = await collection.insert_one(document)
        
        return {
            "success": True,
            "roadmap_id": str(result.inserted_id),
            "message": "Career roadmap replaced successfully (previous roadmap deleted)",
            "is_replacement": True
        }
    else:
        # Create new roadmap
        document["created_at"] = datetime.utcnow()
        result = await collection.insert_one(document)
        
        return {
            "success": True,
            "roadmap_id": str(result.inserted_id),
            "message": "Career roadmap saved successfully",
            "is_replacement": False
        }


async def get_career_roadmap_by_user_id(user_id: str) -> Optional[dict]:
    """
    Get the career roadmap for a user.
    Each user has only one active roadmap.
    
    Args:
        user_id: The user's ID
    
    Returns:
        The roadmap document or None if not found
    """
    if db is None:
        raise Exception("Database not connected")
    
    collection = db.career_roadmaps
    
    document = await collection.find_one({"user_id": user_id})
    
    if document:
        document["_id"] = str(document["_id"])
    
    return document


async def delete_career_roadmap(user_id: str) -> dict:
    """
    Delete a user's career roadmap.
    
    Args:
        user_id: The user's ID
    
    Returns:
        dict with success status
    """
    if db is None:
        raise Exception("Database not connected")
    
    collection = db.career_roadmaps
    result = await collection.delete_one({"user_id": user_id})
    
    return {
        "success": result.deleted_count > 0,
        "message": "Roadmap deleted successfully" if result.deleted_count > 0 else "No roadmap found"
    }
