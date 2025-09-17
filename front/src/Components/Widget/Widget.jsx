import React, { useState, useEffect, useRef } from 'react';
import './Widget.css'

const Widget = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [currentLanguage, setCurrentLanguage] = useState('en');
  const [sessionId, setSessionId] = useState(null);
  const [showWelcome, setShowWelcome] = useState(true);
  const [showNotification, setShowNotification] = useState(false);
  
  const messagesRef = useRef(null);
  const inputRef = useRef(null);
  const apiBaseUrl = 'http://localhost:8000'; // Update this to your API URL

  // Initialize session
  useEffect(() => {
    const newSessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    setSessionId(newSessionId);
    
    // Show welcome notification after 3 seconds
    const timer = setTimeout(() => {
      setShowNotification(true);
    }, 3000);
    
    return () => clearTimeout(timer);
  }, []);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    if (messagesRef.current) {
      messagesRef.current.scrollTop = messagesRef.current.scrollHeight;
    }
  }, [messages, isTyping]);

  // Focus input when chat opens
  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  const toggleChat = () => {
    setIsOpen(!isOpen);
    if (!isOpen) {
      setShowNotification(false);
    }
  };

  const closeChat = () => {
    setIsOpen(false);
  };

  const handleSubmit = async (e) => {
    if (e) e.preventDefault();
    const message = inputMessage.trim();
    if (message && !isTyping) {
      await sendMessage(message);
    }
  };

  const sendMessage = async (message) => {
    if (isTyping) return;

    if (showWelcome) {
      setShowWelcome(false);
    }

    const userMessage = {
      id: Date.now(),
      text: message,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsTyping(true);

    try {
      const response = await fetch(`${apiBaseUrl}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: message,
          language: currentLanguage,
          session_id: sessionId
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      const botMessage = {
        id: Date.now() + 1,
        text: data.response,
        sender: 'bot',
        timestamp: new Date(),
        metadata: {
          confidence: data.confidence,
          language: data.detected_language,
          suggestions: data.suggested_questions || [],
          fallback: data.fallback_to_human
        }
      };

      setMessages(prev => [...prev, botMessage]);
      setSessionId(data.session_id);

    } catch (error) {
      console.error('Error:', error);
      const errorMessage = {
        id: Date.now() + 1,
        text: 'Sorry, I encountered an error. Please try again later.',
        sender: 'bot',
        timestamp: new Date(),
        metadata: {
          confidence: 0,
          language: 'en',
          suggestions: [],
          fallback: true
        }
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleQuestionClick = (question) => {
    if (!isOpen) {
      setIsOpen(true);
    }
    setTimeout(() => {
      sendMessage(question);
    }, 300);
  };

  const popularQuestions = [
    { icon: '📚', text: 'Admission requirements?', question: 'What are the admission requirements?' },
    { icon: '💰', text: 'Fee deadline information?', question: 'When is the fee deadline?' },
    { icon: '📖', text: 'Library timings?', question: 'Library timings?' }
  ];

  const languageOptions = [
    { value: 'en', label: 'EN' },
    { value: 'hi', label: 'हि' },
    { value: 'ta', label: 'த' },
    { value: 'te', label: 'తె' },
    { value: 'kn', label: 'ಕ' },
    { value: 'mr', label: 'म' },
    { value: 'gu', label: 'ગુ' },
    { value: 'bn', label: 'বা' }
  ];

  return (
    <>
      {/* Chat Widget Container */}
      <div className="chat-widget-container">
        {/* Chat Bubble */}
        <div 
          className={`chat-bubble ${isOpen ? 'chat-bubble-open' : ''}`}
          onClick={toggleChat}
        >
          <div className={`chat-bubble-icon ${isOpen ? 'chat-bubble-icon-rotated' : ''}`}>
            💬
          </div>
          
          {/* Notification Badge */}
          {showNotification && !isOpen && (
            <div className="notification-badge">1</div>
          )}
          
          {/* Status Dot */}
          <div className="status-dot"></div>
        </div>

        {/* Chat Window */}
        {isOpen && (
          <div className={`chat-window ${isOpen ? 'chat-window-open' : 'chat-window-closed'}`}>
            {/* Chat Header */}
            <div className="chat-header">
              {/* Language Selector */}
              <select 
                className="language-selector"
                value={currentLanguage}
                onChange={(e) => setCurrentLanguage(e.target.value)}
              >
                {languageOptions.map(option => (
                  <option key={option.value} value={option.value} className="language-option">
                    {option.label}
                  </option>
                ))}
              </select>
              
              <div className="header-info">
                <div className="header-avatar">🎓</div>
                <div className="header-text">
                  <h3 className="header-title">Campus Assistant</h3>
                  <p className="header-status">Online • Ready to help</p>
                </div>
              </div>
              
              <button className="close-button" onClick={closeChat}>×</button>
            </div>

            {/* Chat Messages */}
            <div ref={messagesRef} className="chat-messages" style={{ maxHeight: '340px' }}>
              {/* Welcome Message */}
              {showWelcome && (
                <div className="welcome-section">
                  <h3 className="welcome-title">Welcome to Campus Assistant Phoenix!</h3>
                  <p className="welcome-description">I can help you with admissions, fees, schedules, and more.</p>
                  
                  <div className="quick-questions-container">
                    <h4 className="quick-questions-title">Quick Questions</h4>
                    {popularQuestions.map((q, index) => (
                      <div 
                        key={index}
                        className="quick-question-item"
                        onClick={() => handleQuestionClick(q.question)}
                      >
                        {q.icon} {q.text}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Messages */}
              {messages.map((message) => (
                <div 
                  key={message.id}
                  className={`message-wrapper ${message.sender === 'user' ? 'message-wrapper-user' : 'message-wrapper-bot'}`}
                >
                  <div className={`message-avatar ${message.sender === 'user' ? 'avatar-user' : 'avatar-bot'}`}>
                    {message.sender === 'user' ? '👤' : '🤖'}
                  </div>
                  
                  <div className={`message-content ${message.sender === 'user' ? 'message-user' : 'message-bot'}`}>
                    {message.text}
                    
                    {message.sender === 'bot' && message.metadata && (
                      <>
                        <div className="message-confidence">
                          Confidence: {Math.round(message.metadata.confidence * 100)}%
                        </div>
                        
                        {message.metadata.suggestions && message.metadata.suggestions.length > 0 && (
                          <div className="suggestions-section">
                            <h4 className="suggestions-title">You might also ask:</h4>
                            {message.metadata.suggestions.map((suggestion, idx) => (
                              <span
                                key={idx}
                                className="suggestion-chip"
                                onClick={() => sendMessage(suggestion)}
                              >
                                {suggestion}
                              </span>
                            ))}
                          </div>
                        )}
                      </>
                    )}
                  </div>
                </div>
              ))}

              {/* Typing Indicator */}
              {isTyping && (
                <div className="typing-indicator">
                  <div className="typing-avatar">🤖</div>
                  <div className="typing-dots">
                    <div className="typing-dot" style={{ animationDelay: '0s' }}></div>
                    <div className="typing-dot" style={{ animationDelay: '0.2s' }}></div>
                    <div className="typing-dot" style={{ animationDelay: '0.4s' }}></div>
                  </div>
                </div>
              )}
            </div>

            {/* Chat Input */}
            <div className="chat-input-section">
              <div className="input-container">
                <textarea
                  ref={inputRef}
                  className="chat-input"
                  placeholder="Ask me anything..."
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  rows="1"
                  style={{
                    height: 'auto',
                    minHeight: '40px'
                  }}
                />
                <button
                  className="send-button"
                  disabled={isTyping || !inputMessage.trim()}
                  onClick={handleSubmit}
                >
                  →
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </>
  );
};

export default Widget;
