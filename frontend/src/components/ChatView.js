import React, { useState, useRef, useEffect, useContext } from 'react';
import ChatMessage from './ChatMessage';
import { ChatContext } from '../context/chatContext';
import { MdSend } from 'react-icons/md';
import 'react-tooltip/dist/react-tooltip.css';
import { fetchRecipe, askQuestion } from '../apiService';

const ChatView = () => {
  const messagesEndRef = useRef();
  const inputRef = useRef();
  const [formValue, setFormValue] = useState('');
  const [messages, addMessage] = useContext(ChatContext);
  const [isFetchingRecipe, setIsFetchingRecipe] = useState(true);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const updateMessage = (newValue, ai = false) => {
    const id = Date.now() + Math.floor(Math.random() * 1000000);
    const newMsg = {
      id: id,
      createdAt: Date.now(),
      text: newValue,
      ai: ai,
    };

    addMessage(newMsg);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formValue) return;

    const cleanInput = formValue.trim();
    setFormValue('');
    updateMessage(cleanInput, false);

    try {
      if (isFetchingRecipe) {
        const data = await fetchRecipe(cleanInput);
        updateMessage(data.recipe_data, true);
        setIsFetchingRecipe(false);
      } else {
        const response = await askQuestion(cleanInput);
        updateMessage(response.response, true);
      }
    } catch (error) {
      console.error('Failed to process request:', error);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      handleSubmit(e);
      inputRef.current.style.height = 'auto';
    }
  };

  const handleChange = (event) => {
    setFormValue(event.target.value);
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    inputRef.current.focus();
  }, []);

  useEffect(() => {
    inputRef.current.style.height = 'auto';
    inputRef.current.style.height = inputRef.current.scrollHeight + 'px';
  }, [formValue]);

  return (
    <div className="chatview">
      <main className="chatview__chatarea">
        {messages.map((message, index) => (
          <ChatMessage key={index} message={{ ...message }} />
        ))}
        <span ref={messagesEndRef}></span>
      </main>
      <form className="form" onSubmit={handleSubmit}>
        <div className="flex items-stretch justify-between w-full">
          <textarea
            ref={inputRef}
            className="chatview__textarea-message"
            rows={1}
            value={formValue}
            onKeyDown={handleKeyDown}
            onChange={handleChange}
            placeholder={isFetchingRecipe ? "Enter YouTube video URL" : "Ask a question"}
          />
          <button type="submit" className="chatview__btn-send" disabled={!formValue}>
            <MdSend size={30} />
          </button>
        </div>
      </form>
    </div>
  );
};

export default ChatView;
