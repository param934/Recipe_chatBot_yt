import React, { useState } from 'react';
import RecipeForm from './RecipeForm';
import ChatInterface from './ChatInterface';

function App() {
    const [recipeData, setRecipeData] = useState(null);

    return (
        <div>
            <h1>Recipe ChatBot</h1>
            {!recipeData ? (
                <RecipeForm setRecipeData={setRecipeData} />
            ) : (
                <ChatInterface recipeData={recipeData} />
            )}
        </div>
    );
}

export default App;
