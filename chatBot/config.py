import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # MongoDB Configuration
    MONGODB_URL: str = "mongodb+srv://raghavanmuthuraj_db_user:raghav@cluster0.ym3lqdw.mongodb.net/"
    DATABASE_NAME: str = "campus_chatbot"
    
    # Collections
    FAQ_COLLECTION: str = "faqs"
    CONVERSATIONS_COLLECTION: str = "conversations"
    FEEDBACK_COLLECTION: str = "feedback"
    USERS_COLLECTION: str = "users"
    
    # NLP Configuration
    HF_MODEL_NAME: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    CONFIDENCE_THRESHOLD: float = 0.7
    
    # Supported Languages
    SUPPORTED_LANGUAGES: List[str] = [
        "en",  # English
        "hi",  # Hindi
        "ta",  # Tamil
        "te",  # Telugu
        "kn",  # Kannada
        "mr",  # Marathi
        "gu",  # Gujarati
        "bn",  # Bengali
    ]
    
    # Language Names Mapping
    LANGUAGE_NAMES: dict = {
        "en": "English",
        "hi": "हिन्दी",
        "ta": "தமிழ்",
        "te": "తెలుగు",
        "kn": "ಕನ್ನಡ",
        "mr": "मराठी",
        "gu": "ગુજરાતી",
        "bn": "বাংলা",
    }
    
    # API Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # Security
    SECRET_KEY: str = "LxTCRdbrqJnPakM4ekAdC31CBF_R7BlN8o0oBKOoz4o"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Campus Specific
    COLLEGE_NAME: str = "Campus University"
    ADMIN_EMAIL: str = "admin@campus.edu"
    SUPPORT_CONTACT: str = "+91-XXXXXXXXXX"
    
    class Config:
        env_file = ".env"

settings = Settings()