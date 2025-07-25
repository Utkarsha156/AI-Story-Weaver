import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import apiClient from '../../api';
import "./chat.css";

const Chat = ({ token }) => {
    const [messages, setMessages] = useState([
        { role: 'assistant', content: "Hello! Let's create a story. For making the story what genre are you thinking of?", timestamp: new Date() }
    ]);
    const [input, setInput] = useState('');
    const [storyId, setStoryId] = useState(null);
    const [isTyping, setIsTyping] = useState(false);
    const navigate = useNavigate();
    const messagesEndRef = useRef(null);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    const sendMessage = async () => {
        if (!input.trim() || isTyping) return;

        const userMessage = { role: 'user', content: input, timestamp: new Date() };
        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setIsTyping(true);

        try {
            const response = await apiClient.post('/chat', {
                message: input,
                story_id: storyId
            });

            const { response: aiResponse, story_id: newStoryId, status } = response.data;
            
            setStoryId(newStoryId);
            setMessages(prev => [...prev, { role: 'assistant', content: aiResponse, timestamp: new Date() }]);

            if (status === 'generating') {
                setTimeout(() => navigate(`/story/${newStoryId}`), 2000);
            }

        } catch (error) {
            console.error("Chat error:", error);
            if (error.response?.status !== 401) {
               setMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, something went wrong.', timestamp: new Date() }]);
            }
        } finally {
            setIsTyping(false);
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
          e.preventDefault(); 
          sendMessage();
        }
    };

    return (
        <div className="chat-container">
            <div className="chat-header">
                <h2>Let's chat and create!</h2>
                <p>Tell me about your story idea, we'll create a Indian theme story</p>
            </div>
            <div className="chat-messages">
                {messages.map((msg, index) => (
                    <div key={index} className={`message ${msg.role}`}>
                        <div className="message-content">
                            <div className="message-text">{msg.content}</div>
                            <div className="message-time">
                                {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                            </div>
                        </div>
                    </div>
                ))}

                {isTyping && (
                  <div className="message assistant">
                    <div className="message-content">
                      <div className="typing-indicator">
                        <span></span>
                        <span></span>
                        <span></span>
                      </div>
                    </div>
                  </div>
                )}
                
                <div ref={messagesEndRef} />
            </div>
            <div className="chat-input">
                <textarea
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Type your message..."
                    rows="2"
                    disabled={isTyping}
                />
                <button 
                    onClick={sendMessage} 
                    disabled={isTyping || !input.trim()}
                >
                    Send
                </button>
            </div>
        </div>
    );
};

export default Chat;