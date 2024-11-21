import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { io } from 'socket.io-client';

function ChatInterface({ recipeData }) {
    const [question, setQuestion] = useState('');
    const [messages, setMessages] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const socketRef = useRef(null);
    const responseEndRef = useRef(null);

    // Auto-scroll to the latest message
    useEffect(() => {
        responseEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    useEffect(() => {
        socketRef.current = io(process.env.REACT_APP_BACKEND_URL, {
            transports: ['websocket'],
            cors: {
                origin: "http://localhost:3000",
                credentials: true,
            },
        });

        socketRef.current.on('connect', () => {
            console.log('Connected to server');
        });

        socketRef.current.on('response', (data) => {
            console.log('Received response:', data); // Debug log
            
            if (data.content) {
                setMessages(prev => {
                    const newMessages = [...prev];
                    const lastMessage = newMessages[newMessages.length - 1];
                    
                    if (lastMessage && lastMessage.role === 'assistant') {
                        lastMessage.content += data.content;
                    } else {
                        newMessages.push({ role: 'assistant', content: data.content });
                    }
                    
                    return newMessages;
                });
            } else if (data.error) {
                setIsLoading(false);
                alert(data.error);
            }
        });

        socketRef.current.on('stream_start', () => {
            console.log('Stream started'); // Debug log
            setIsLoading(true);
        });

        socketRef.current.on('stream_end', () => {
            console.log('Stream ended'); // Debug log
            setIsLoading(false);
        });

        return () => {
            if (socketRef.current) {
                socketRef.current.disconnect();
            }
        };
    }, []);

    const handleQuestion = () => {
        if (!question.trim()) return;

        setMessages((prev) => [...prev, { role: 'user', content: question }]);
        setIsLoading(true);
        socketRef.current.emit('ask_question', { question });
        setQuestion(''); // Clear input after sending
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleQuestion();
        }
    };

    return (
        <div className="chat-interface">
            <h3>Recipe Details:</h3>
            <pre className="recipe-data">{recipeData}</pre>

            <div className="chat-container">
                <div className="messages">
                    {messages.map((msg, index) => (
                        <div
                            key={index}
                            className={`message-bubble ${msg.role === 'user' ? 'user' : 'assistant'}`}
                        >
                            {msg.content}
                        </div>
                    ))}
                    {isLoading && <div className="typing-indicator">Assistant is typing...</div>}
                    <div ref={responseEndRef} />
                </div>

                <div className="input-container">
                    <textarea
                        value={question}
                        onChange={(e) => setQuestion(e.target.value)}
                        onKeyPress={handleKeyPress}
                        placeholder="Ask a question about the recipe"
                        disabled={isLoading}
                    />
                    <button
                        onClick={handleQuestion}
                        disabled={isLoading || !question.trim()}
                    >
                        {isLoading ? 'Processing...' : 'Ask'}
                    </button>
                </div>
            </div>

            <style jsx>{`
                .chat-interface {
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                }

                .recipe-data {
                    background: #f5f5f5;
                    padding: 15px;
                    border-radius: 8px;
                    margin-bottom: 20px;
                }

                .chat-container {
                    display: flex;
                    flex-direction: column;
                    gap: 20px;
                }

                .messages {
                    max-height: 400px;
                    overflow-y: auto;
                    padding: 10px;
                    border: 1px solid #ddd;
                    border-radius: 8px;
                    background: #fafafa;
                }

                .message-bubble {
                    margin-bottom: 10px;
                    padding: 10px;
                    border-radius: 8px;
                    max-width: 70%;
                }

                .message-bubble.user {
                    background: #007bff;
                    color: white;
                    margin-left: auto;
                }

                .message-bubble.assistant {
                    background: #f1f1f1;
                    color: #333;
                }

                .typing-indicator {
                    color: gray;
                    font-style: italic;
                }

                .input-container {
                    display: flex;
                    gap: 10px;
                }

                textarea {
                    flex: 1;
                    min-height: 50px;
                    padding: 10px;
                    border-radius: 8px;
                    border: 1px solid #ddd;
                    resize: vertical;
                }

                button {
                    padding: 10px 20px;
                    background: #007bff;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    cursor: pointer;
                }

                button:disabled {
                    background: #ccc;
                }
            `}</style>
        </div>
    );
}

export default ChatInterface;
