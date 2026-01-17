"""
Script to wipe all data from MongoDB collections
Run this script to clear all user data and start fresh
"""

import asyncio
import sys
import os

# Add the parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings


async def wipe_database():
    """Wipe all collections in the database"""
    print(f"Connecting to MongoDB: {settings.mongodb_url}")
    print(f"Database: {settings.mongodb_db_name}")
    
    # Confirm before wiping
    confirmation = input("\n⚠️  WARNING: This will DELETE ALL DATA in the database!\n"
                        "Are you sure you want to continue? (type 'yes' to confirm): ")
    
    if confirmation.lower() != 'yes':
        print("Operation cancelled.")
        return
    
    try:
        client = AsyncIOMotorClient(settings.mongodb_url)
        db = client[settings.mongodb_db_name]
        
        # List of collections to wipe
        collections = [
            "User",
            "LearningSession", 
            "Assessment",
            "AssessmentResponse",
            "Feedback",
            "KnowledgeChunk",
            "LearnerProfile",
        ]
        
        print("\n🗑️  Wiping collections...")
        
        for collection_name in collections:
            result = await db[collection_name].delete_many({})
            print(f"   ✓ {collection_name}: Deleted {result.deleted_count} documents")
        
        # Also drop any other collections that might exist
        all_collections = await db.list_collection_names()
        for col in all_collections:
            if col not in collections:
                result = await db[col].delete_many({})
                print(f"   ✓ {col}: Deleted {result.deleted_count} documents")
        
        print("\n✅ Database wiped successfully!")
        print("   You can now start fresh with new data.\n")
        
        client.close()
        
    except Exception as e:
        print(f"\n❌ Error wiping database: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(wipe_database())
