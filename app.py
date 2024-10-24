from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
import requests
import base64
from pymongo.server_api import ServerApi
from openai import OpenAI
import json
import os
from dotenv import load_dotenv
from bson.objectid import ObjectId
import pycountry
from function import private

app = Flask(__name__)

# Connect to MongoDB
uri = "mongodb+srv://Bamidele1:1631324de@mycluster.vffurcu.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(uri, server_api=ServerApi('1'))
db = client['test']
messages_collection = db['chat']

load_dotenv()

api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI()



def generate_image(prompt):
    try:
        response = client.images.generate(
          model="dall-e-3",
          prompt=prompt,
          n=1,
          size="1024x1024"
        )
        image_urls = [img.url for img in response.data]  # Extract URLs for all images
        return image_urls

    except Exception as e:
        print(f"Error generating image: {str(e)}")
        return None

def collect_user_responses(user_id):
    user_messages = messages_collection.find({'user_id': user_id, 'sender': 'user'}).sort('_id', -1).limit(2)
    user_responses = [msg['message'] for msg in user_messages]  # Collect only user messages
    return " ".join(user_responses)  # Combine responses into a single prompt




def extract_question_answers(paired_messages):
    # Create an empty dictionary to store the results
    question_answer_dict = {}

    # Loop through each message
    for message in paired_messages:
        # Split the string into question and answer
        if ': ' in message:
            question, answer = message.split(': ', 1)
            # Store the question as the key and the answer as the value
            question_answer_dict[question] = answer

    # Return the dictionary of question-answer pairs
    return question_answer_dict


def get_last_entry(user_id):
    results = []

    for i in range(6):
        # Find the last bot message
        last_entry_bot = messages_collection.find({'user_id': user_id, "sender": "bot"}).sort('_id', -1).skip(i).limit(
            1)
        bot_message = None
        if last_entry_bot:  # Ensure there's at least one message
            bot_message = last_entry_bot[0].get("message")

        last_entry_user = messages_collection.find({'user_id': user_id, "sender": "user"}).sort('_id', -1).skip(
            i).limit(1)
        user_message = None
        if last_entry_user:
            user_message = last_entry_user[0].get("message")

        # Append the paired message to results if both exist
        if bot_message and user_message:
            results.append(f"{bot_message}: {user_message}")

    return results

EXCHANGE_RATE_API_KEY = "216eefb93b366047c5e8cda7"
EXCHANGE_RATE_API_URL = f"https://v6.exchangerate-api.com/v6/216eefb93b366047c5e8cda7/latest/USD"

def get_currency_code(country_name):
    try:
        # Use pycountry to get the country object
        country = pycountry.countries.get(name=country_name)
        if not country:
            return None

        # Use pycountry to get the currency object associated with the country
        currency = pycountry.currencies.get(numeric=country.numeric)
        if not currency:
            return None

        # Return the currency code
        return currency.alpha_3
    except Exception as e:
        return None

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

questions = [
    "Can you tell me your name?",
    "What career do you dream of pursuing after high school?",
    "What hobbies or activities make you lose track of time?",
    "Is there a global issue or cause you're passionate about?",
    "What kind of art or media inspires you the most?",
    "If your future had a color palette, what colors would it include?",
    "What's the biggest challenge you think you'll face in achieving your dreams?",

]

message_counter = 0

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/send_message', methods=['POST'])
def send_message():
    user_message = request.json.get('message')
    user_id = request.json.get('user_id')

    # Fetch all previous messages for the user from the database
    user_data = messages_collection.find_one({'user_id': user_id,"First": "first"})

    # Check if the user has a message counter saved or it's their first time
    if user_data:
        message_counter = user_data.get('message_counter', 0)  # Default to 0 if not set
        first_session_completed = user_data.get('first_session_completed', False)
    else:
        message_counter = 0  # New user starts from the first question
        first_session_completed = False

    # Skip the "Can you tell me your name?" for the first session
    if not first_session_completed and message_counter == 0:
        message_counter += 1  # Skip the first question about name
        messages_collection.insert_one({
            'user_id': user_id,
            'message': "What is your name?",
            'sender': 'bot'
        })

    if message_counter < len(questions):
        # Select the appropriate question to ask
        response = questions[message_counter]

        message_counter += 1

        # Save user message and bot response to the database
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

        # Update the user's message_counter and first session status in the database
        messages_collection.update_one(
            {'user_id': user_id,
             "First":"first"},
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
            {'user_id': user_id,
             "First": "first"},
            {'$set': {
                'message_counter': 0,
                'first_session_completed': True
            }},
            upsert=True
        )
        # User has answered all questions, generate an image based on responses
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

        # Save the generated image message
        if image_url:
            # # Save the image response to the database
            # messages_collection.insert_one({
            #     'user_id': user_id,
            #     'message': images,
            #     'sender': 'bot'
            # })
            # print(images)


            # Send the image to the frontend
            return jsonify({
                "response": "Here is the image generated from your answers.",
                "image": image_url
            })
        else:
            return jsonify({"response": "Sorry, I couldn't generate the image."})



@app.route('/load_messages/<user_id>', methods=['GET'])
def load_messages(user_id):
    messages = messages_collection.find({'user_id': int(user_id)})
    response = [{'message': msg['message'], 'sender': msg['sender']} for msg in messages if 'message' in msg and 'sender' in msg]
    print(response)
    return jsonify(response)

@app.route('/get-rate', methods=['POST'])
def get_exchange_rate():
    # Get the country name from the POST request data
    data = request.get_json()
    country_name = data.get('country_name')

    if not country_name:
        return jsonify({"error": "Country name is required"}), 400

    # Get the currency code from the country name
    currency_code = get_currency_code(country_name)

    if not currency_code:
        return jsonify({"error": "Invalid country name or no currency found"}), 400

    # Get exchange rates from the API
    try:
        response = requests.get(EXCHANGE_RATE_API_URL)
        response_data = response.json()

        # Check if the API request was successful
        if response.status_code != 200:
            return jsonify({"error": "Failed to fetch exchange rates"}), 500

        # Extract the rate for the given currency
        exchange_rate = response_data['conversion_rates'].get(currency_code)

        if not exchange_rate:
            return jsonify({"error": "Invalid currency code"}), 400

        # Return the exchange rate as JSON
        return jsonify({
            "country_name": country_name,
            "currency_code": currency_code,
            "exchange_rate_to_usd": exchange_rate
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

