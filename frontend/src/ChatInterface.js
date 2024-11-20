import React, { useState } from 'react';
import axios from 'axios';

function ChatInterface({ recipeData }) {
    const [question, setQuestion] = useState('');
    const [response, setResponse] = useState('');

    const handleQuestion = async () => {
        try {
            const res = await axios.post(`${process.env.REACT_APP_BACKEND_URL}/ask_question`, { question });
            setResponse(res.data.response);
        } catch (error) {
            alert(error.response?.data?.error || "Error processing question");
        }
    };

    return (
        <div>
            <h3>Recipe Details:</h3>
            <pre>{recipeData}</pre>
            <input
                type="text"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="Ask a question about the recipe"
            />
            <button onClick={handleQuestion}>Ask</button>
            {response && <p>Response: {response}</p>}
        </div>
    );
}

export default ChatInterface;
