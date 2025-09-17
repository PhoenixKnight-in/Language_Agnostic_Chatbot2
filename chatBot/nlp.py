import asyncio
from typing import List, Tuple, Dict, Optional
import logging
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from googletrans import Translator
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException
import re
import numpy as np
import torch

# Fixed imports - using relative imports for services directory
from config import settings
from model import FAQ

logger = logging.getLogger(__name__)

class NLPService:
    def __init__(self):
        self.model = None
        self.translator = None
        self.faq_embeddings = None
        self.faqs = []
        self.is_initialized = False
    
    async def initialize(self):
        """Initialize NLP models and components"""
        try:
            logger.info("Initializing NLP Service...")
            
            # Load sentence transformer model
            self.model = SentenceTransformer(settings.HF_MODEL_NAME)
            
            # Initialize translator
            self.translator = Translator()
            
            self.is_initialized = True
            logger.info("NLP Service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize NLP Service: {e}")
            raise
    
    def detect_language(self, text: str) -> Tuple[str, float]:
        """Detect language of input text"""
        try:
            # Clean text for better detection
            cleaned_text = self.clean_text(text)
            
            if len(cleaned_text.strip()) < 3:
                return "en", 0.5  # Default to English for very short text
            
            detected_lang = detect(cleaned_text)
            
            # Map detected language to supported languages
            if detected_lang in settings.SUPPORTED_LANGUAGES:
                return detected_lang, 0.9
            
            # If detected language is not supported, try to map it
            lang_mapping = {
                'ur': 'hi',  # Urdu -> Hindi
                'ne': 'hi',  # Nepali -> Hindi
                'sa': 'hi',  # Sanskrit -> Hindi
            }
            
            mapped_lang = lang_mapping.get(detected_lang, "en")
            return mapped_lang, 0.7
            
        except LangDetectException as e:
            logger.warning(f"Language detection failed: {e}")
            return "en", 0.5  # Default to English
    
    def clean_text(self, text: str) -> str:
        """Clean and preprocess text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove special characters but keep essential punctuation
        text = re.sub(r'[^\w\s\?\!\.\,\-\'\"]', '', text)
        
        return text
    
    async def translate_text(self, text: str, target_language: str, source_language: str = "auto") -> str:
        """Translate text to target language"""
        try:
            if target_language == source_language or target_language == "auto":
                return text
            
            # Use asyncio to make blocking call async
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, 
                lambda: self.translator.translate(text, src=source_language, dest=target_language)
            )
            
            return result.text if result else text
            
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return text  # Return original text if translation fails
    
    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for a list of texts"""
        if not self.is_initialized:
            raise RuntimeError("NLP Service not initialized")
        
        return self.model.encode(texts)
    
    async def update_faq_embeddings(self, faqs: List[FAQ]):
        """Update FAQ embeddings for similarity search"""
        try:
            self.faqs = faqs
            
            # Prepare texts for embedding (questions in multiple languages)
            all_questions = []
            for faq in faqs:
                # Add English question
                all_questions.append(faq.question)
                
                # Add questions in other languages
                for lang, content in faq.languages.items():
                    if 'question' in content and content['question']:
                        all_questions.append(content['question'])
            
            if all_questions:
                # Generate embeddings
                loop = asyncio.get_event_loop()
                self.faq_embeddings = await loop.run_in_executor(
                    None, self.generate_embeddings, all_questions
                )
                logger.info(f"Generated embeddings for {len(all_questions)} FAQ questions")
            
        except Exception as e:
            logger.error(f"Failed to update FAQ embeddings: {e}")
            raise
    
    async def find_best_match(self, user_query: str, language: str = "en", top_k: int = 3) -> List[Tuple[FAQ, float, str]]:
        """Find best matching FAQ for user query"""
        try:
            if not self.faqs or self.faq_embeddings is None:
                logger.warning("No FAQs or embeddings available")
                return []
            
            # Generate embedding for user query
            loop = asyncio.get_event_loop()
            query_embedding = await loop.run_in_executor(
                None, self.generate_embeddings, [user_query]
            )
            
            # Calculate similarities
            similarities = cosine_similarity(query_embedding, self.faq_embeddings)[0]
            
            # Get top matches
            top_indices = np.argsort(similarities)[-top_k:][::-1]
            
            matches = []
            question_index = 0
            
            for idx in top_indices:
                similarity_score = similarities[idx]
                
                if similarity_score < settings.CONFIDENCE_THRESHOLD:
                    continue
                
                # Find which FAQ this question belongs to
                current_idx = 0
                matched_faq = None
                matched_question = ""
                
                for faq in self.faqs:
                    # Check English question
                    if current_idx == idx:
                        matched_faq = faq
                        matched_question = faq.question
                        break
                    current_idx += 1
                    
                    # Check other language questions
                    for lang, content in faq.languages.items():
                        if current_idx == idx and 'question' in content:
                            matched_faq = faq
                            matched_question = content['question']
                            break
                        current_idx += 1
                    
                    if matched_faq:
                        break
                
                if matched_faq:
                    matches.append((matched_faq, similarity_score, matched_question))
            
            return matches
            
        except Exception as e:
            logger.error(f"Error finding best match: {e}")
            return []
    
    async def generate_response(self, faq: FAQ, user_language: str) -> str:
        """Generate response in user's preferred language"""
        try:
            # Check if answer exists in user's language
            if user_language in faq.languages and 'answer' in faq.languages[user_language]:
                return faq.languages[user_language]['answer']
            
            # If not available in user's language, translate from English
            if user_language != "en":
                return await self.translate_text(faq.answer, user_language, "en")
            
            return faq.answer
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return faq.answer  # Return English answer as fallback
    
    def extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text for categorization"""
        # Simple keyword extraction - can be enhanced with more sophisticated methods
        text = self.clean_text(text.lower())
        
        # Common stop words (simplified)
        stop_words = {'is', 'are', 'was', 'were', 'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'what', 'when', 'where', 'how', 'why', 'who'}
        
        words = text.split()
        keywords = [word for word in words if len(word) > 2 and word not in stop_words]
        
        return keywords[:10]  # Return top 10 keywords
    
    def categorize_query(self, text: str, keywords: List[str] = None) -> Optional[str]:
        """Categorize user query based on keywords"""
        if not keywords:
            keywords = self.extract_keywords(text)
        
        # Category mappings
        category_keywords = {
            'admissions': ['admission', 'apply', 'application', 'eligibility', 'entrance', 'course', 'program', 'degree'],
            'fees': ['fee', 'fees', 'payment', 'cost', 'tuition', 'scholarship', 'financial'],
            'academics': ['exam', 'result', 'grade', 'syllabus', 'curriculum', 'subject', 'marks', 'semester'],
            'schedule': ['schedule', 'timetable', 'class', 'timing', 'calendar', 'holiday', 'break'],
            'facilities': ['library', 'hostel', 'canteen', 'laboratory', 'sports', 'facility', 'transport'],
            'placement': ['placement', 'job', 'career', 'internship', 'company', 'recruitment'],
            'contact': ['contact', 'phone', 'email', 'address', 'office', 'hours', 'location']
        }
        
        keyword_scores = {}
        for category, cat_keywords in category_keywords.items():
            score = sum(1 for kw in keywords if any(ck in kw.lower() for ck in cat_keywords))
            if score > 0:
                keyword_scores[category] = score
        
        if keyword_scores:
            return max(keyword_scores, key=keyword_scores.get)
        
        return None
    
    async def generate_suggestions(self, category: str = None, language: str = "en") -> List[str]:
        """Generate suggested questions based on category"""
        suggestions = []
        
        try:
            # Filter FAQs by category if provided
            relevant_faqs = [faq for faq in self.faqs if not category or faq.category == category]
            
            # Select top 3-5 popular questions
            for faq in relevant_faqs[:5]:
                if language in faq.languages and 'question' in faq.languages[language]:
                    suggestions.append(faq.languages[language]['question'])
                else:
                    # Translate question if not available in user's language
                    translated_question = await self.translate_text(faq.question, language, "en")
                    suggestions.append(translated_question)
        
        except Exception as e:
            logger.error(f"Error generating suggestions: {e}")
        
        return suggestions[:3]  # Return top 3 suggestions

# Global NLP service instance
nlp_service = NLPService()