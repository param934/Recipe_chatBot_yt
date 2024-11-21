# Generalized Prompts
NUTRITION_PROMPT = """
You are a dietitian. Analyze the recipe details below to calculate the nutritional values (calories, protein, carbs, fat, fiber, vitamins). Provide per-serving and total values if applicable. Answer only what is asked.

Recipe Details:
{recipe_data}

User Question:
{user_question}
"""

SUBSTITUTION_PROMPT = """
You are an expert chef. Suggest substitutions for missing or allergenic ingredients in the recipe, with brief explanations of why these substitutions work and Answer only what is asked.

Recipe Details:
{recipe_data}

User Question:
{user_question}
"""

PROCEDURE_PROMPT = """
You are a culinary expert. Clarify doubts based on the user's question. Provide step-by-step guidance.

Recipe Details:
{recipe_data}

User Question:
{user_question}
"""

GENERAL_PROMPT = """
You are a recipe assistant. Answer the user's question accurately based on the recipe details.

Recipe Details:
{recipe_data}

User Question:
{user_question}
"""

DIETARY_PROMPT = """
You are a specialized nutritionist. Suggest recipe adjustments for the specified dietary requirement (e.g., vegan, keto, gluten-free). Provide relevant substitutions or removals.

Recipe Details:
{recipe_data}

User Question:
{user_question}
"""

STORAGE_PROMPT = """
You are a food storage expert. Provide details on how to store the dish, its shelf life, freezing options, and reheating instructions.

Recipe Details:
{recipe_data}

User Question:
{user_question}
"""

SAFETY_PROMPT = """
You are a food safety expert. Answer the user's question about food safety, including proper cooking, handling, or ingredient freshness.

Recipe Details:
{recipe_data}

User Question:
{user_question}
"""

FLAVOR_PROMPT = """
You are a flavor expert. Suggest ways to enhance or adjust the flavor of the recipe (e.g., spiciness, sweetness, balancing).

Recipe Details:
{recipe_data}

User Question:
{user_question}
"""

CULTURAL_PROMPT = """
You are a culinary historian. Provide cultural or historical context for the recipe, such as its origin or traditional significance.

Recipe Details:
{recipe_data}

User Question:
{user_question}
"""

# Define categories and their related keywords
CATEGORY_KEYWORDS = {
    "nutrition": [
        "calorie", "protein", "carb", "fat", "vitamin", 
        "nutrition", "health", "macro", "nutrient","healty"
    ],
    "substitution": [
        "replace", "swap", "alternative", 
        "substitute", "allergy", "cannot eat"
    ],
    "procedure": [
        "cook", "prepare", "step", "method", 
        "technique", "instruction", "how","Summary","simplify"
    ],
    "dietary": [
        "vegan", "vegetarian", "keto", 
        "gluten-free", "diet", "restriction"
    ],
    "storage": [
        "store", "freeze", "refrigerate", 
        "preserve", "shelf life", "keep"
    ],
    "flavor": [
        "taste", "spicy", "sweet", "season", 
        "flavor", "enhance", "adjust"
    ],
    "cultural": [
        "origin", "history", "culture", 
        "traditional", "background"
    ],
    "safety": [
        "safe", "raw", "cook", "temperature", 
        "handling", "food safety"
    ]
}
from fuzzywuzzy import process
import warnings
import logging
import re
from pytube import YouTube
from youtube_transcript_api import YouTubeTranscriptApi
from langchain_community.llms.ollama import Ollama
import asyncio

# Suppress warnings and logging for cleaner output
warnings.filterwarnings("ignore")
logging.getLogger("transformers").setLevel(logging.ERROR)

# Step 1: Transcript Extraction
def get_video_transcript(video_url):
    """
    Fetch and clean the transcript of a YouTube video.
    """
    try:
        video = YouTube(video_url)
        video_id = video.video_id
        # Fetch transcript
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        # Combine and clean transcript
        full_transcript = ' '.join([item['text'] for item in transcript])
        cleaned_transcript = re.sub(r'\[.*?\]', '', full_transcript)
        return cleaned_transcript
    except Exception as e:
        return f"Error fetching transcript: {e}"

# Step 2: Recipe Extraction Prompt
EXTRACTION_PROMPT = """
You are a professional chef assistant. Extract the following information from the provided recipe transcript:

1. **Title**: The concise name of the recipe.
2. **Ingredients**: List all ingredients with their quantities.
3. **Procedure**: Step-by-step cooking instructions.

Transcript:
{transcript}
"""

# Step 3: Query LLAMA for Extraction
def query_llm(prompt, model="llama3"):
    """
    Queries the LLAMA 3 model using Ollama with the given prompt.
    """
    try:
        print("Trying")
        model_instance = Ollama(model=model)
        print("lamma 3")
        response = model_instance.invoke(prompt)

        print("REsponse")
        return response.strip()
    except Exception as e:
        return f"Error querying LLM: {e}"

def extract_recipe(transcript):
    """
    Extract structured recipe data using LLM.
    """
    prompt = EXTRACTION_PROMPT.format(transcript=transcript)
    return query_llm(prompt)

import asyncio

async def query_llm_stream(prompt, model="llama3", websocket=None):
    """
    Queries the LLAMA model and streams the response over WebSocket.
    Also prints the response to the CLI.
    """
    try:
        model_instance = Ollama(model=model)
        # We expect a synchronous generator from this method
        response_stream = model_instance.stream(prompt)
        
        # Use asyncio to iterate through the chunks synchronously
        for chunk in response_stream:
            # Check if chunk is a dictionary or a string
            if isinstance(chunk, dict):
                chunk_text = chunk.get('text', '')
            else:
                chunk_text = chunk
            
            # Print each chunk to the CLI
            print(chunk_text, end='', flush=True)
            
            # Send each chunk of text progressively to the WebSocket client
            if websocket:
                await websocket.send(chunk_text)

    except Exception as e:
        if websocket:
            await websocket.send(f"Error querying LLM: {e}")
        print(f"Error querying LLM: {e}")




# Recipe ChatBot Class
class RecipeChatBot:
    def __init__(self, model="llama3"):
        self.model = model
        self.recipe_data = None
        self.conversation_history = []

    def fetch_recipe(self, video_url):
        """
        Extract and process recipe details from a YouTube video.
        """
        transcript = get_video_transcript(video_url)
        print(transcript)
        if "Error" in transcript:
            print(transcript)
            return transcript

        self.recipe_data = extract_recipe(transcript)
        
        return self.recipe_data

    def introduce_and_display_recipe(self):
        """
        Introduce the bot and display recipe details.
        """
        if not self.recipe_data:
            return "Error: Recipe data is missing. Please provide a valid video URL."
        
        introduction = (
            "Hi! I'm your Recipe Assistant. I can help you understand, modify, or get insights about recipes.\n"
            "Here’s the recipe I extracted for you:"
        )
        return f"{introduction}\n\n{self.recipe_data}\n\nFeel free to ask me any questions about the recipe!"

    def classify_question(self,question):
        """
        Classify the user's question into one of the predefined categories using fuzzy matching
        and priority rules to handle overlapping matches.
        """
        question_lower = question.lower()
        match_scores = {}

        # Perform fuzzy matching for each category and store the scores
        for category, keywords in CATEGORY_KEYWORDS.items():
            match, score = process.extractOne(question_lower, keywords)
            match_scores[category] = score

        # Sort categories by match score in descending order
        sorted_categories = sorted(match_scores.items(), key=lambda x: x[1], reverse=True)

        # Handle cases with conflicting matches
        # If the top two categories have close scores, apply additional logic
        if len(sorted_categories) > 1:
            top_category, top_score = sorted_categories[0]
            second_category, second_score = sorted_categories[1]

            # If scores are close, prioritize based on specificity
            if abs(top_score - second_score) < 10:  # Adjust this threshold as needed
                # Define a priority order for overlapping categories
                category_priority = [
                    "procedure", "substitution", "nutrition", "dietary", 
                    "storage", "safety", "flavor", "cultural", "general"
                ]

                # Return the category with higher priority
                for category in category_priority:
                    if top_category == category or second_category == category:
                        print("----> "+category)
                        return category
        # print("----> "+sorted_categories[0][0] if sorted_categories else "general")
        # If there's no close match or only one strong match, return the top category
        return sorted_categories[0][0] if sorted_categories else "general"


    def ask_question(self, question):
        """
        Generate a response to the user's question based on the classified intent.
        """
        if not self.recipe_data:
            return "Please fetch a recipe first by providing a video URL."

        # Determine the appropriate prompt
        intent = self.classify_question(question)
        prompt_mapping = {
            "nutrition": NUTRITION_PROMPT,
            "substitution": SUBSTITUTION_PROMPT,
            "procedure": PROCEDURE_PROMPT,
            "dietary": DIETARY_PROMPT,
            "storage": STORAGE_PROMPT,
            "flavor": FLAVOR_PROMPT,
            "cultural": CULTURAL_PROMPT,
            "safety": SAFETY_PROMPT,
            "general": GENERAL_PROMPT,
        }
        prompt = prompt_mapping[intent].format(recipe_data=self.recipe_data, user_question=question)
        # print("===Promot==="+prompt)
        # Query the LLM
        # response = query_llm(prompt, model=self.model)
        response=asyncio.run(query_llm_stream(prompt, model=self.model))
        # Update conversation history
        self.conversation_history.append({"role": "user", "content": question})
        self.conversation_history.append({"role": "assistant", "content": response})

        return response

    def display_conversation(self):
        """
        Display the conversation history.
        """
        for turn in self.conversation_history:
            role = turn["role"].capitalize()
            print(f"{role}: {turn['content']}")

# Main Script
if __name__ == "__main__":
    bot = RecipeChatBot()

    print("Welcome to the Recipe ChatBot!")
    print("Provide a YouTube link to get started.")

    # Step 1: Fetch Recipe
    video_url = input("Enter YouTube video URL: ").strip()
    recipe_data = bot.fetch_recipe(video_url)

    if "Error" in recipe_data:
        print("Failed to fetch recipe. Please try again with a different video.")
    else:
        print(bot.introduce_and_display_recipe())

        # Step 2: Ask Questions in a Loop
        while True:
            user_question = input("\nYour Question (or type 'exit' to quit): ").strip()
            if user_question.lower() == "exit":
                print("Thank you for using the Recipe ChatBot! Goodbye.")
                break

            response = bot.ask_question(user_question)
            # print("\nAssistant:", response)
