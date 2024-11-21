from flask import Flask, request, jsonify, copy_current_request_context
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from recipe_chatbot import RecipeChatBot 
import asyncio

app = Flask(__name__)

# Configure Flask app
app.config['DEBUG'] = True
app.config['USE_RELOADER'] = False  # Disable reloader

# Allow cross-origin requests from your React app
CORS(app, resources={r"/*": {"origins": "http://localhost:3000", "supports_credentials": True}})

# Initialize SocketIO with additional configuration
socketio = SocketIO(
    app,
    cors_allowed_origins="http://localhost:3000",
    async_mode='eventlet',  # Use eventlet as async mode
    logger=False,  # Disable socketio logging
    engineio_logger=False  # Disable engineio logging
)

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

@socketio.on('ask_question')
def handle_ask_question(data):
    print("Received ask_question event")
    
    question = data.get('question')
    if not chatbot.recipe_data:
        emit('response', {"error": "Please fetch a recipe first."})
        return

    emit('stream_start')  # Signal the start of streaming

    @copy_current_request_context
    def async_task():
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            def stream_handler(event, data):
                emit(event, data)
            
            loop.run_until_complete(chatbot.ask_question(question, stream_handler))
            emit('stream_end')  # Signal the end of streaming
            
        except Exception as e:
            print(f"Error in async task: {e}")
            emit('response', {"error": str(e)})
            emit('stream_end')
        finally:
            loop.close()

    socketio.start_background_task(async_task)

if __name__ == '__main__':
    socketio.run(
        app,
        debug=False,  # Disable debug mode for the socket
        use_reloader=False,  # Disable reloader
        allow_unsafe_werkzeug=True,
        host='0.0.0.0',
        port=5000
    )
