from flask import Flask, request, jsonify
from flask_cors import CORS
from recipe_chatbot import RecipeChatBot 

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests for React

# Initialize the chatbot
chatbot = RecipeChatBot()

@app.route('/fetch_recipe', methods=['POST'])
def fetch_recipe():
    data = request.json
    video_url = data.get('video_url')
    if not video_url:
        return jsonify({"error": "Video URL is required"}), 400
    
    recipe_data = chatbot.fetch_recipe(video_url)
    if "Error" in recipe_data:
        return jsonify({"error": recipe_data}), 500
    
    return jsonify({"recipe_data": recipe_data})

@app.route('/ask_question', methods=['POST'])
def ask_question():
    data = request.json
    question = data.get('question')
    if not chatbot.recipe_data:
        return jsonify({"error": "Please fetch a recipe first."}), 400

    response = chatbot.ask_question(question)
    print(response)
    return jsonify({"response": response})

if __name__ == '__main__':
    app.run(debug=True)
