import motor.motor_asyncio
from config import settings
from model import FAQ, ConversationLog, Feedback, User
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.client = None
        self.db = None
    
    async def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGODB_URL)
            self.db = self.client[settings.DATABASE_NAME]
            
            # Test connection
            await self.client.admin.command('ping')
            logger.info(f"Connected to MongoDB: {settings.DATABASE_NAME}")
            
            # Create indexes
            await self.create_indexes()
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    async def create_indexes(self):
        """Create database indexes for better performance"""
        try:
            # FAQ Collection indexes
            await self.db[settings.FAQ_COLLECTION].create_index([("category", 1)])
            await self.db[settings.FAQ_COLLECTION].create_index([("keywords", 1)])
            await self.db[settings.FAQ_COLLECTION].create_index([("is_active", 1)])
            
            # Conversations Collection indexes
            await self.db[settings.CONVERSATIONS_COLLECTION].create_index([("session_id", 1)])
            await self.db[settings.CONVERSATIONS_COLLECTION].create_index([("timestamp", -1)])
            await self.db[settings.CONVERSATIONS_COLLECTION].create_index([("detected_language", 1)])
            
            # Users Collection indexes
            await self.db[settings.USERS_COLLECTION].create_index([("user_id", 1)], unique=True)
            await self.db[settings.USERS_COLLECTION].create_index([("last_active", -1)])
            
            # Feedback Collection indexes
            await self.db[settings.FEEDBACK_COLLECTION].create_index([("session_id", 1)])
            await self.db[settings.FEEDBACK_COLLECTION].create_index([("timestamp", -1)])
            
            logger.info("Database indexes created successfully")
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")

    async def close(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            logger.info("Database connection closed")

    # FAQ Operations
    async def insert_faq(self, faq: FAQ) -> str:
        """Insert a new FAQ"""
        result = await self.db[settings.FAQ_COLLECTION].insert_one(faq.dict(exclude={"id"}))
        return str(result.inserted_id)

    async def get_all_faqs(self, active_only: bool = True) -> List[FAQ]:
        """Get all FAQs"""
        query = {"is_active": True} if active_only else {}
        cursor = self.db[settings.FAQ_COLLECTION].find(query)
        faqs = []
        async for doc in cursor:
            faqs.append(FAQ(**doc))
        return faqs

    async def search_faqs(self, category: Optional[str] = None, keywords: Optional[List[str]] = None) -> List[FAQ]:
        """Search FAQs by category or keywords"""
        query = {"is_active": True}
        
        if category:
            query["category"] = category
        
        if keywords:
            query["keywords"] = {"$in": keywords}
        
        cursor = self.db[settings.FAQ_COLLECTION].find(query)
        faqs = []
        async for doc in cursor:
            faqs.append(FAQ(**doc))
        return faqs

    async def update_faq(self, faq_id: str, update_data: Dict[str, Any]) -> bool:
        """Update an FAQ"""
        from datetime import datetime
        update_data["updated_at"] = datetime.now()
        result = await self.db[settings.FAQ_COLLECTION].update_one(
            {"_id": faq_id}, {"$set": update_data}
        )
        return result.modified_count > 0

    async def delete_faq(self, faq_id: str) -> bool:
        """Soft delete an FAQ"""
        result = await self.db[settings.FAQ_COLLECTION].update_one(
            {"_id": faq_id}, {"$set": {"is_active": False}}
        )
        return result.modified_count > 0

    # Conversation Operations
    async def log_conversation(self, conversation: ConversationLog) -> str:
        """Log a conversation"""
        result = await self.db[settings.CONVERSATIONS_COLLECTION].insert_one(
            conversation.dict(exclude={"id"})
        )
        return str(result.inserted_id)

    async def get_conversation_history(self, session_id: str, limit: int = 10) -> List[ConversationLog]:
        """Get conversation history for a session"""
        cursor = self.db[settings.CONVERSATIONS_COLLECTION].find(
            {"session_id": session_id}
        ).sort("timestamp", -1).limit(limit)
        
        conversations = []
        async for doc in cursor:
            conversations.append(ConversationLog(**doc))
        return conversations

    async def get_recent_conversations(self, hours: int = 24) -> List[ConversationLog]:
        """Get recent conversations"""
        from datetime import datetime, timedelta
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        cursor = self.db[settings.CONVERSATIONS_COLLECTION].find(
            {"timestamp": {"$gte": cutoff_time}}
        ).sort("timestamp", -1)
        
        conversations = []
        async for doc in cursor:
            conversations.append(ConversationLog(**doc))
        return conversations

    # User Operations
    async def create_or_update_user(self, user: User) -> str:
        """Create or update a user"""
        existing_user = await self.db[settings.USERS_COLLECTION].find_one(
            {"user_id": user.user_id}
        )
        
        if existing_user:
            # Update existing user
            from datetime import datetime
            await self.db[settings.USERS_COLLECTION].update_one(
                {"user_id": user.user_id},
                {
                    "$set": {"last_active": datetime.now()},
                    "$inc": {"total_conversations": 1}
                }
            )
            return str(existing_user["_id"])
        else:
            # Create new user
            result = await self.db[settings.USERS_COLLECTION].insert_one(
                user.dict(exclude={"id"})
            )
            return str(result.inserted_id)

    async def get_user(self, user_id: str) -> Optional[User]:
        """Get a user by user_id"""
        doc = await self.db[settings.USERS_COLLECTION].find_one({"user_id": user_id})
        return User(**doc) if doc else None

    # Feedback Operations
    async def save_feedback(self, feedback: Feedback) -> str:
        """Save user feedback"""
        result = await self.db[settings.FEEDBACK_COLLECTION].insert_one(
            feedback.dict(exclude={"id"})
        )
        return str(result.inserted_id)

    async def get_feedback_stats(self) -> Dict[str, Any]:
        """Get feedback statistics"""
        pipeline = [
            {
                "$group": {
                    "_id": None,
                    "avg_rating": {"$avg": "$rating"},
                    "total_feedback": {"$sum": 1},
                    "rating_distribution": {
                        "$push": "$rating"
                    }
                }
            }
        ]
        
        result = await self.db[settings.FEEDBACK_COLLECTION].aggregate(pipeline).to_list(1)
        if result:
            stats = result[0]
            # Calculate rating distribution
            ratings = stats["rating_distribution"]
            distribution = {i: ratings.count(i) for i in range(1, 6)}
            
            return {
                "average_rating": round(stats["avg_rating"], 2),
                "total_feedback": stats["total_feedback"],
                "rating_distribution": distribution
            }
        return {"average_rating": 0, "total_feedback": 0, "rating_distribution": {}}

    # Analytics Operations
    async def get_conversation_stats(self, days: int = 30) -> Dict[str, Any]:
        """Get conversation statistics"""
        from datetime import datetime, timedelta
        start_date = datetime.now() - timedelta(days=days)
        
        pipeline = [
            {"$match": {"timestamp": {"$gte": start_date}}},
            {
                "$group": {
                    "_id": None,
                    "total_conversations": {"$sum": 1},
                    "unique_sessions": {"$addToSet": "$session_id"},
                    "languages": {"$push": "$detected_language"},
                    "categories": {"$push": "$category"},
                    "avg_confidence": {"$avg": "$confidence"},
                    "fallback_count": {
                        "$sum": {"$cond": ["$fallback_triggered", 1, 0]}
                    },
                    "avg_response_time": {"$avg": "$response_time_ms"}
                }
            }
        ]
        
        result = await self.db[settings.CONVERSATIONS_COLLECTION].aggregate(pipeline).to_list(1)
        if result:
            stats = result[0]
            languages = stats["languages"]
            categories = [c for c in stats["categories"] if c]  # Filter out None values
            
            return {
                "total_conversations": stats["total_conversations"],
                "unique_sessions": len(stats["unique_sessions"]),
                "languages_used": {lang: languages.count(lang) for lang in set(languages)},
                "categories_queried": {cat: categories.count(cat) for cat in set(categories)} if categories else {},
                "average_confidence": round(stats["avg_confidence"], 2),
                "fallback_rate": round(stats["fallback_count"] / stats["total_conversations"] * 100, 2) if stats["total_conversations"] > 0 else 0,
                "average_response_time": round(stats["avg_response_time"], 2) if stats["avg_response_time"] else 0
            }
        
        return {
            "total_conversations": 0,
            "unique_sessions": 0,
            "languages_used": {},
            "categories_queried": {},
            "average_confidence": 0,
            "fallback_rate": 0,
            "average_response_time": 0
        }

# Global database instance
db = Database()