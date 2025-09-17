import asyncio
import uuid
import time
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import logging

# Fixed imports - using relative imports for services directory
from model import ChatMessage, ChatResponse, ConversationLog, User
from nlp import nlp_service
from database import db
from config import settings

logger = logging.getLogger(__name__)

class ChatbotService:
    def __init__(self):
        self.active_sessions = {}  # Store session contexts
        self.fallback_responses = {
            "en": {
                "no_match": "I'm sorry, I couldn't find a specific answer to your question. Let me connect you with a human assistant. You can contact our support at {contact}.",
                "greeting": "Hello! I'm your campus assistant. How can I help you today?",
                "farewell": "Thank you for using our service! Have a great day!",
                "error": "I encountered an error while processing your request. Please try again or contact support."
            },
            "hi": {
                "no_match": "क्षमा करें, मुझे आपके प्रश्न का विशिष्ट उत्तर नहीं मिला। मैं आपको एक मानव सहायक से जोड़ता हूँ। आप हमारे सपोर्ट से {contact} पर संपर्क कर सकते हैं।",
                "greeting": "नमस्ते! मैं आपका कैंपस सहायक हूँ। आज मैं आपकी कैसे मदद कर सकता हूँ?",
                "farewell": "हमारी सेवा का उपयोग करने के लिए धन्यवाद! आपका दिन शुभ हो!",
                "error": "आपके अनुरोध को संसाधित करते समय मुझे एक त्रुटि का सामना करना पड़ा। कृपया पुनः प्रयास करें या सपोर्ट से संपर्क करें।"
            }
        }
    
    async def process_message(self, message: ChatMessage) -> ChatResponse:
        """Process incoming chat message and generate response"""
        start_time = time.time()
        
        try:
            # Generate session ID if not provided
            session_id = message.session_id or str(uuid.uuid4())
            message_id = str(uuid.uuid4())
            
            # Detect language if auto
            detected_language, lang_confidence = nlp_service.detect_language(message.message)
            if message.language != "auto":
                detected_language = message.language
            
            # Update session context
            await self._update_session_context(session_id, message.message, detected_language)
            
            # Check for greeting or farewell
            if self._is_greeting(message.message):
                response_text = self._get_fallback_response("greeting", detected_language)
                suggestions = await nlp_service.generate_suggestions(language=detected_language)
                
                response = ChatResponse(
                    response=response_text,
                    confidence=1.0,
                    detected_language=detected_language,
                    session_id=session_id,
                    message_id=message_id,
                    suggested_questions=suggestions
                )
                
                # Log conversation
                await self._log_conversation(message, response, start_time, fallback=False)
                return response
            
            if self._is_farewell(message.message):
                response_text = self._get_fallback_response("farewell", detected_language)
                
                response = ChatResponse(
                    response=response_text,
                    confidence=1.0,
                    detected_language=detected_language,
                    session_id=session_id,
                    message_id=message_id
                )
                
                # Clear session context
                if session_id in self.active_sessions:
                    del self.active_sessions[session_id]
                
                # Log conversation
                await self._log_conversation(message, response, start_time, fallback=False)
                return response
            
            # Find best matching FAQ
            matches = await nlp_service.find_best_match(
                message.message, 
                detected_language, 
                top_k=3
            )
            
            if matches and matches[0][1] >= settings.CONFIDENCE_THRESHOLD:
                # Found good match
                best_faq, confidence, matched_question = matches[0]
                
                # Generate response in user's language
                response_text = await nlp_service.generate_response(best_faq, detected_language)
                
                # Generate suggestions
                suggestions = await nlp_service.generate_suggestions(
                    best_faq.category, 
                    detected_language
                )
                
                response = ChatResponse(
                    response=response_text,
                    confidence=confidence,
                    detected_language=detected_language,
                    session_id=session_id,
                    message_id=message_id,
                    category=best_faq.category,
                    suggested_questions=suggestions
                )
                
                # Log conversation
                await self._log_conversation(message, response, start_time, fallback=False)
                return response
            
            else:
                # No good match found - fallback to human
                response_text = self._get_fallback_response("no_match", detected_language).format(
                    contact=settings.SUPPORT_CONTACT
                )
                
                # Try to categorize query for better suggestions
                category = nlp_service.categorize_query(message.message)
                suggestions = await nlp_service.generate_suggestions(category, detected_language)
                
                response = ChatResponse(
                    response=response_text,
                    confidence=0.0,
                    detected_language=detected_language,
                    session_id=session_id,
                    message_id=message_id,
                    fallback_to_human=True,
                    suggested_questions=suggestions,
                    category=category
                )
                
                # Log conversation
                await self._log_conversation(message, response, start_time, fallback=True)
                return response
        
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            
            # Return error response
            session_id = message.session_id or str(uuid.uuid4())
            message_id = str(uuid.uuid4())
            detected_language = "en"  # Default to English for errors
            
            response = ChatResponse(
                response=self._get_fallback_response("error", detected_language),
                confidence=0.0,
                detected_language=detected_language,
                session_id=session_id,
                message_id=message_id,
                fallback_to_human=True
            )
            
            return response
    
    async def _update_session_context(self, session_id: str, message: str, language: str):
        """Update session context for conversation continuity"""
        if session_id not in self.active_sessions:
            self.active_sessions[session_id] = {
                "messages": [],
                "language": language,
                "last_category": None,
                "created_at": datetime.now()
            }
        
        # Add message to context (keep last 5 messages)
        self.active_sessions[session_id]["messages"].append({
            "text": message,
            "timestamp": datetime.now(),
            "language": language
        })
        
        # Keep only last 5 messages
        if len(self.active_sessions[session_id]["messages"]) > 5:
            self.active_sessions[session_id]["messages"] = self.active_sessions[session_id]["messages"][-5:]
    
    async def _log_conversation(self, message: ChatMessage, response: ChatResponse, start_time: float, fallback: bool = False):
        """Log conversation to database"""
        try:
            response_time = int((time.time() - start_time) * 1000)  # Convert to milliseconds
            
            conversation_log = ConversationLog(
                session_id=response.session_id,
                message_id=response.message_id,
                user_id=message.user_id,
                user_message=message.message,
                bot_response=response.response,
                detected_language=response.detected_language,
                confidence=response.confidence,
                category=response.category,
                fallback_triggered=fallback,
                response_time_ms=response_time
            )
            
            await db.log_conversation(conversation_log)
            
            # Update user if user_id provided
            if message.user_id:
                user = User(
                    user_id=message.user_id,
                    preferred_language=response.detected_language
                )
                await db.create_or_update_user(user)
        
        except Exception as e:
            logger.error(f"Error logging conversation: {e}")
    
    def _is_greeting(self, message: str) -> bool:
        """Check if message is a greeting"""
        greetings = [
            # English
            "hello", "hi", "hey", "good morning", "good afternoon", "good evening",
            # Hindi
            "नमस्ते", "नमस्कार", "हैलो", "हाय",
            # Tamil
            "வணக்கம்", "ஹலோ",
            # Telugu
            "నమస్కారం", "హలో",
            # Kannada
            "ನಮಸ್ಕಾರ", "ಹಲೋ",
            # Marathi
            "नमस्कार", "हॅलो",
            # Gujarati
            "નમસ્તે", "હેલો",
            # Bengali
            "নমস্কার", "হ্যালো"
        ]
        
        message_lower = message.lower().strip()
        return any(greeting in message_lower for greeting in greetings)
    
    def _is_farewell(self, message: str) -> bool:
        """Check if message is a farewell"""
        farewells = [
            # English
            "bye", "goodbye", "see you", "thanks", "thank you", "that's all",
            # Hindi
            "अलविदा", "धन्यवाद", "बाय", "गुडबाय",
            # Tamil
            "பாய்", "நன்றி",
            # Telugu
            "బై", "ధన్యవాదాలు",
            # Kannada
            "ಬೈ", "ಧನ್ಯವಾದಗಳು",
            # Marathi
            "बाय", "धन्यवाद",
            # Gujarati
            "બાય", "આભાર",
            # Bengali
            "বাই", "ধন্যবাদ"
        ]
        
        message_lower = message.lower().strip()
        return any(farewell in message_lower for farewell in farewells)
    
    def _get_fallback_response(self, response_type: str, language: str) -> str:
        """Get fallback response in specified language"""
        if language in self.fallback_responses and response_type in self.fallback_responses[language]:
            return self.fallback_responses[language][response_type]
        
        # Default to English
        return self.fallback_responses["en"].get(response_type, "I'm sorry, I couldn't process your request.")
    
    async def get_session_history(self, session_id: str) -> List[Dict]:
        """Get conversation history for a session"""
        try:
            conversations = await db.get_conversation_history(session_id, limit=20)
            
            history = []
            for conv in conversations:
                history.append({
                    "user_message": conv.user_message,
                    "bot_response": conv.bot_response,
                    "timestamp": conv.timestamp,
                    "confidence": conv.confidence,
                    "language": conv.detected_language
                })
            
            return history[::-1]  # Return in chronological order
        
        except Exception as e:
            logger.error(f"Error getting session history: {e}")
            return []
    
    async def get_popular_questions(self, language: str = "en", category: str = None) -> List[str]:
        """Get popular questions based on conversation logs"""
        try:
            # This could be enhanced with actual analytics
            return await nlp_service.generate_suggestions(category, language)
        
        except Exception as e:
            logger.error(f"Error getting popular questions: {e}")
            return []

# Global chatbot service instance
chatbot_service = ChatbotService()