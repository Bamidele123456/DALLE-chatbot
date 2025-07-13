# DALLE Chatbot

A Flask-based web application that chats with users, collects their responses, and generates AI art prompts for DALL-E image generation. The app stores conversations in MongoDB and can email prompts for privacy assurance. It features a modern frontend with a left navbar and responsive design.

## Features
- Conversational AI chatbot (OpenAI)
- DALL-E image generation from user responses
- MongoDB for chat history
- Email notification for privacy
- Responsive web UI (HTML/CSS/JS)

## Project Structure
```
DALLE-chatbot/
├── app.py                # Main Flask app
├── function.py           # Email utility
├── requirements.txt      # Python dependencies
├── static/               # Static assets (CSS, JS, images)
│   ├── style.css
│   ├── script.js
│   └── images/
├── templates/
│   └── index.html        # Main HTML template
├── downloaded_images/    # Generated/downloaded images
```

## Setup Instructions
1. **Clone the repository**
2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
3. **Set up environment variables**
   - Create a `.env` file in the root directory with:
     ```env
     OPENAI_API_KEY=your_openai_api_key
     MONGODB_URI=your_mongodb_uri
     ```
   - Replace with your actual API keys and MongoDB URI.
4. **Run the app**
   ```bash
   python app.py
   ```
   The app will be available at `http://localhost:8080`.

## Usage
- Open the app in your browser.
- Chat with the AI; your responses will be used to generate an art prompt.
- After answering all questions, an AI-generated image will be displayed.

## Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key for chat and image generation.
- `MONGODB_URI`: MongoDB connection string.

## Notes
- All user responses are stored in MongoDB for session continuity.
- Email credentials are currently hardcoded in `function.py` for demo purposes. For production, move them to environment variables.
- Test/demo scripts have been removed for clarity.

## License
MIT 