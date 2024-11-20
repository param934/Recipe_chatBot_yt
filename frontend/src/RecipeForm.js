import React, { useState } from 'react';
import axios from 'axios';

function RecipeForm({ setRecipeData }) {
    const [videoUrl, setVideoUrl] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const response = await axios.post(`${process.env.REACT_APP_BACKEND_URL}/fetch_recipe`, {
                video_url: videoUrl,
            });
            setRecipeData(response.data.recipe_data);
        } catch (error) {
            alert(error.response?.data?.error || "Error fetching recipe");
        }
    };

    return (
        <form onSubmit={handleSubmit}>
            <input
                type="text"
                value={videoUrl}
                onChange={(e) => setVideoUrl(e.target.value)}
                placeholder="Enter YouTube video URL"
                required
            />
            <button type="submit">Fetch Recipe</button>
        </form>
    );
}

export default RecipeForm;
