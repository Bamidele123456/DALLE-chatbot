from flask import Blueprint, render_template, request, jsonify
from pymongo import MongoClient
import requests
from pymongo.server_api import ServerApi
from openai import OpenAI
import os
from bson.objectid import ObjectId
import pycountry
from function import private

main = Blueprint('main', __name__)

# Connect to MongoDB
uri = os.getenv('MONGODB_URI', '')
client = MongoClient(uri, server_api=ServerApi('1'))
db = client['test']
messages_collection = db['chat']

api_key = os.getenv('OPENAI_API_KEY')
openai_client = OpenAI()


def generate_image(prompt):
    try:
        response = openai_client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            size="1024x1024"
        )
        image_urls = [img.url for img in response.data]
        return image_urls
    except Exception as e:
        print(f"Error generating image: {str(e)}")
        return None

def extract_question_answers(paired_messages):
    question_answer_dict = {}
    for message in paired_messages:
        if ': ' in message:
            question, answer = message.split(': ', 1)
            question_answer_dict[question] = answer
    return question_answer_dict

def get_last_entry(user_id):
    results = []
    for i in range(6):
        last_entry_bot = messages_collection.find({'user_id': user_id, "sender": "bot"}).sort('_id', -1).skip(i).limit(1)
        bot_message = None
        if last_entry_bot:
            bot_message = last_entry_bot[0].get("message")
        last_entry_user = messages_collection.find({'user_id': user_id, "sender": "user"}).sort('_id', -1).skip(i).limit(1)
        user_message = None
        if last_entry_user:
            user_message = last_entry_user[0].get("message")
        if bot_message and user_message:
            results.append(f"{bot_message}: {user_message}")
    return results

EXCHANGE_RATE_API_URL = "https://v6.exchangerate-api.com/v6/216eefb93b366047c5e8cda7/latest/USD"

def get_currency_code(country_name):
    try:
        country = pycountry.countries.get(name=country_name)
        if not country:
            return None
        currency = pycountry.currencies.get(numeric=country.numeric)
        if not currency:
            return None
        return currency.alpha_3
    except Exception:
        return None

questions = [
    "Can you tell me your name?",
    "What career do you dream of pursuing after high school?",
    "What hobbies or activities make you lose track of time?",
    "Is there a global issue or cause you're passionate about?",
    "What kind of art or media inspires you the most?",
    "If your future had a color palette, what colors would it include?",
    "What's the biggest challenge you think you'll face in achieving your dreams?",
]

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/send_message', methods=['POST'])
def send_message():
    user_message = request.json.get('message')
    user_id = request.json.get('user_id')
    user_data = messages_collection.find_one({'user_id': user_id, "First": "first"})
    if user_data:
        message_counter = user_data.get('message_counter', 0)
        first_session_completed = user_data.get('first_session_completed', False)
    else:
        message_counter = 0
        first_session_completed = False
    if not first_session_completed and message_counter == 0:
        message_counter += 1
        messages_collection.insert_one({
            'user_id': user_id,
            'message': "What is your name?",
            'sender': 'bot'
        })
    if message_counter < len(questions):
        response = questions[message_counter]
        message_counter += 1
        messages_collection.insert_one({
            'user_id': user_id,
            'message': user_message,
            'sender': 'user'
        })
        messages_collection.insert_one({
            'user_id': user_id,
            'message': response,
            'sender': 'bot'
        })
        messages_collection.update_one(
            {'user_id': user_id, "First": "first"},
            {'$set': {
                'message_counter': message_counter,
                'first_session_completed': True
            }},
            upsert=True
        )
        return jsonify({"response": response})
    else:
        messages_collection.insert_one({
            'user_id': user_id,
            'message': user_message,
            'sender': 'user'
        })
        messages_collection.update_one(
            {'user_id': user_id, "First": "first"},
            {'$set': {
                'message_counter': 0,
                'first_session_completed': True
            }},
            upsert=True
        )
        last_entry = get_last_entry(user_id)
        qa_dict = extract_question_answers(last_entry)
        dream_career = qa_dict.get("What career do you dream of pursuing after high school?")
        global_issue = qa_dict.get("Is there a global issue or cause you're passionate about?")
        challenge = qa_dict.get("What's the biggest challenge you think you'll face in achieving your dreams?")
        inspire = qa_dict.get("What kind of art or media inspires you the most?")
        color_palette = qa_dict.get("If your future had a color palette, what colors would it include?")
        media = qa_dict.get("What kind of art or media inspires you the most?")
        prompts_use = f"Create a vibrant A sharp, high-resolution image illustration of a high school student standing confidently, representing their aspirations {dream_career},Icons illustrating {global_issue}, Artistic styles inspired by {inspire},A color palette featuring {color_palette}, A challenge represented as {challenge},showing this media {media}"
        private(prompts_use)
        image_url = generate_image(prompts_use)
        if image_url:
            return jsonify({
                "response": "Here is the image generated from your answers.",
                "image": image_url
            })
        else:
            return jsonify({"response": "Sorry, I couldn't generate the image."})

@main.route('/load_messages/<user_id>', methods=['GET'])
def load_messages(user_id):
    messages = messages_collection.find({'user_id': int(user_id)})
    response = [{'message': msg['message'], 'sender': msg['sender']} for msg in messages if 'message' in msg and 'sender' in msg]
    return jsonify(response)

@main.route('/get-rate', methods=['POST'])
def get_exchange_rate():
    data = request.get_json()
    country_name = data.get('country_name')
    if not country_name:
        return jsonify({"error": "Country name is required"}), 400
    currency_code = get_currency_code(country_name)
    if not currency_code:
        return jsonify({"error": "Invalid country name or no currency found"}), 400
    try:
        response = requests.get(EXCHANGE_RATE_API_URL)
        response_data = response.json()
        if response.status_code != 200:
            return jsonify({"error": "Failed to fetch exchange rates"}), 500
        exchange_rate = response_data['conversion_rates'].get(currency_code)
        if not exchange_rate:
            return jsonify({"error": "Invalid currency code"}), 400
        return jsonify({
            "country_name": country_name,
            "currency_code": currency_code,
            "exchange_rate_to_usd": exchange_rate
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500 