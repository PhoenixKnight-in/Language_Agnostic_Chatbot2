from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
import uvicorn
import logging
from datetime import datetime
import os

# Import our modules
from config import settings
from model import ChatMessage, ChatResponse, FeedbackRequest, ConversationStats
from database import db
from nlp import nlp_service
from chatbot_service import chatbot_service
from data_seeder import DataSeeder

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting Campus Chatbot Application...")
    
    try:
        # Initialize database
        await db.connect()
        logger.info("Database connected successfully")
        
        # Initialize NLP service
        await nlp_service.initialize()
        logger.info("NLP service initialized successfully")
        
        # Seed sample data (uncomment for first run)
        # await data_seeder.seed_sample_faqs()
        
        # Load FAQs and create embeddings
        faqs = await db.get_all_faqs()
        await nlp_service.update_faq_embeddings(faqs)
        logger.info(f"Loaded {len(faqs)} FAQs and created embeddings")
        
        logger.info("Application startup completed successfully!")
        
    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    try:
        await db.close()
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")
    logger.info("Application shutdown completed")

# Create FastAPI app
app = FastAPI(
    title="Campus Multilingual Chatbot",
    description="A multilingual chatbot for campus queries supporting Hindi, English, and regional languages",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files and templates
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

templates = None
if os.path.exists("templates"):
    templates = Jinja2Templates(directory="templates")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        db_status = "connected" if hasattr(db, 'client') and db.client else "disconnected"
        nlp_status = "ready" if hasattr(nlp_service, 'is_initialized') and nlp_service.is_initialized else "not ready"
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "services": {
                "database": db_status,
                "nlp_service": nlp_status
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )

# Main chat endpoint
@app.post("/chat", response_model=ChatResponse)
async def chat(message: ChatMessage):
    """Main chat endpoint for processing user messages"""
    try:
        logger.info(f"Processing message: {message.message[:50]}...")
        response = await chatbot_service.process_message(message)
        logger.info(f"Generated response with confidence: {response.confidence}")
        return response
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Language detection endpoint
@app.post("/detect-language")
async def detect_language(request: dict):
    """Detect language of input text"""
    try:
        text = request.get("text", "")
        if not text:
            raise HTTPException(status_code=400, detail="Text is required")
        
        detected_lang, confidence = nlp_service.detect_language(text)
        
        return {
            "detected_language": detected_lang,
            "confidence": confidence,
            "supported": detected_lang in settings.SUPPORTED_LANGUAGES,
            "language_name": settings.LANGUAGE_NAMES.get(detected_lang, detected_lang)
        }
        
    except Exception as e:
        logger.error(f"Error in language detection: {e}")
        raise HTTPException(status_code=500, detail=f"Language detection failed: {str(e)}")

# Get conversation history
@app.get("/conversation/{session_id}")
async def get_conversation_history(session_id: str):
    """Get conversation history for a session"""
    try:
        history = await chatbot_service.get_session_history(session_id)
        return {"session_id": session_id, "history": history}
        
    except Exception as e:
        logger.error(f"Error getting conversation history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get conversation history: {str(e)}")

# Submit feedback
@app.post("/feedback")
async def submit_feedback(feedback: FeedbackRequest):
    """Submit user feedback"""
    try:
        from model import Feedback
        feedback_obj = Feedback(
            session_id=feedback.session_id,
            message_id=feedback.message_id,
            rating=feedback.rating,
            comment=feedback.comment
        )
        
        feedback_id = await db.save_feedback(feedback_obj)
        logger.info(f"Feedback saved with ID: {feedback_id}")
        
        return {"message": "Feedback submitted successfully", "feedback_id": str(feedback_id)}
        
    except Exception as e:
        logger.error(f"Error submitting feedback: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to submit feedback: {str(e)}")

# Get popular questions
@app.get("/popular-questions")
async def get_popular_questions(language: str = "en", category: str = None):
    """Get popular questions based on category and language"""
    try:
        questions = await chatbot_service.get_popular_questions(language, category)
        return {
            "language": language,
            "category": category,
            "questions": questions
        }
        
    except Exception as e:
        logger.error(f"Error getting popular questions: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get popular questions: {str(e)}")

# Get supported languages
@app.get("/languages")
async def get_supported_languages():
    """Get list of supported languages"""
    try:
        return {
            "supported_languages": settings.SUPPORTED_LANGUAGES,
            "language_names": settings.LANGUAGE_NAMES
        }
    except Exception as e:
        logger.error(f"Error getting supported languages: {e}")
        return {
            "supported_languages": ["en", "hi", "ta", "te", "kn", "mr", "gu", "bn"],
            "language_names": {
                "en": "English",
                "hi": "हिन्दी",
                "ta": "தமிழ்",
                "te": "తెలుగు",
                "kn": "ಕನ್ನಡ",
                "mr": "मराठी",
                "gu": "ગુજરાતી",
                "bn": "বাংলা"
            }
        }

# Analytics endpoints (for admin dashboard)
@app.get("/analytics/stats")
async def get_analytics_stats(days: int = 30):
    """Get conversation analytics"""
    try:
        stats = await db.get_conversation_stats(days)
        feedback_stats = await db.get_feedback_stats()
        
        return {
            "conversation_stats": stats,
            "feedback_stats": feedback_stats,
            "period_days": days
        }
        
    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")

# Web interface (if templates exist)
@app.get("/", response_class=HTMLResponse)
async def web_interface(request: Request):
    """Web interface for the chatbot"""
    if templates:
        try:
            return templates.TemplateResponse("index.html", {"request": request})
        except Exception as e:
            logger.error(f"Template error: {e}")
            # Fall back to basic HTML
    
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Campus Multilingual Chatbot</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .header { text-align: center; color: #333; margin-bottom: 30px; }
            .api-section { margin: 20px 0; padding: 15px; background: #f8f9fa; border-radius: 5px; }
            .endpoint { font-family: monospace; background: #e9ecef; padding: 5px 10px; border-radius: 3px; }
            .method { color: #28a745; font-weight: bold; }
            .method.post { color: #007bff; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 Campus Multilingual Chatbot</h1>
                <p>RESTful API for campus queries in multiple languages</p>
            </div>
            
            <div class="api-section">
                <h3>Available Endpoints:</h3>
                
                <p><span class="method post">POST</span> <span class="endpoint">/chat</span><br>
                Send a message to the chatbot</p>
                
                <p><span class="method post">POST</span> <span class="endpoint">/detect-language</span><br>
                Detect language of input text</p>
                
                <p><span class="method">GET</span> <span class="endpoint">/conversation/{session_id}</span><br>
                Get conversation history</p>
                
                <p><span class="method post">POST</span> <span class="endpoint">/feedback</span><br>
                Submit user feedback</p>
                
                <p><span class="method">GET</span> <span class="endpoint">/popular-questions</span><br>
                Get popular questions by category</p>
                
                <p><span class="method">GET</span> <span class="endpoint">/languages</span><br>
                Get supported languages</p>
                
                <p><span class="method">GET</span> <span class="endpoint">/health</span><br>
                Health check</p>
                
                <p><span class="method">GET</span> <span class="endpoint">/docs</span><br>
                Interactive API documentation</p>
            </div>
            
            <div class="api-section">
                <h3>Supported Languages:</h3>
                <p>English, हिन्दी, தமிழ், తెలుగు, ಕನ್ನಡ, मराठी, ગુજરાતી, বাংলা</p>
            </div>
            
            <div class="api-section">
                <h3>Example Usage:</h3>
                <pre style="background: #f1f3f4; padding: 15px; border-radius: 5px; overflow-x: auto;">
curl -X POST "http://localhost:8000/chat" \\
     -H "Content-Type: application/json" \\
     -d '{
       "message": "What are the admission requirements?",
       "language": "en"
     }'</pre>
            </div>
        </div>
    </body>
    </html>
    """)

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Endpoint not found", "path": str(request.url)}
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)}
    )

# Background tasks for maintenance
async def refresh_faq_embeddings():
    """Background task to refresh FAQ embeddings periodically"""
    try:
        faqs = await db.get_all_faqs()
        await nlp_service.update_faq_embeddings(faqs)
        logger.info("FAQ embeddings refreshed successfully")
    except Exception as e:
        logger.error(f"Error refreshing FAQ embeddings: {e}")

if __name__ == "__main__":
    # Run the application
    try:
        uvicorn.run(
            "main:app",
            host=settings.HOST,
            port=settings.PORT,
            reload=settings.DEBUG,
            log_level="info"
        )
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        raise