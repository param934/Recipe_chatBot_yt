import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000';

export const fetchRecipe = async (videoUrl) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/fetch_recipe`, { video_url: videoUrl });
    return response.data;
  } catch (error) {
    console.error('Error fetching recipe:', error);
    throw error;
  }
};

export const askQuestion = async (question) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/ask_question`, { question });
    return response.data;
  } catch (error) {
    console.error('Error asking question:', error);
    throw error;
  }
};
