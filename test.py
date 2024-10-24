import os
from dotenv import load_dotenv
from flask import jsonify
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from openai import OpenAI
import json



load_dotenv()
uri = "mongodb+srv://Bamidele1:1631324de@mycluster.vffurcu.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(uri, server_api=ServerApi('1'))
db = client['test']
messages_collection = db['chat']

api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI()

def generate_image(prompt):
    try:
        response = client.images.generate(
          model="dall-e-2",
          prompt=prompt,
          n=5,
          size="1024x1024"
        )
        image_urls = [img.url for img in response.data]  # Extract URLs for all images
        return image_urls

    except Exception as e:
        print(f"Error generating image: {str(e)}")
        return None

def scollect_user_responses(user_id):
    # Fetch messages for the specific user
    user_messages = list(messages_collection.find({'user_id': user_id}))  # Convert cursor to a list

    # Separate bot questions and user responses
    bot_questions = []
    user_responses = []

    for msg in user_messages:
        # Check if 'sender' key exists and process accordingly
        if 'sender' in msg:
            if msg['sender'] == 'bot':
                bot_questions.append(msg['message'])
            elif msg['sender'] == 'user':
                user_responses.append(msg['message'])

    # Combine each question with its corresponding answer
    paired_responses = [f"{q}: {a}" for q, a in zip(bot_questions, user_responses)]

    # Return only the last 6 paired responses
    return paired_responses[-6:]

user_id = 1111
prompt = scollect_user_responses(user_id)
prompts = json.dumps(prompt)
print (prompts)
images = []
image_urls = generate_image(prompts)
if image_urls:
    for i, url in enumerate(image_urls):
        images.append(url)

    urls = ({
        "response": "Here is the image generated from your answers.",
        "image": images
    })



