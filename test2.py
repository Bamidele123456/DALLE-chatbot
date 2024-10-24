from pymongo import MongoClient
import requests
import base64
from pymongo.server_api import ServerApi
import openai

uri = "mongodb+srv://Bamidele1:1631324de@mycluster.vffurcu.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(uri, server_api=ServerApi('1'))
db = client['test']
messages_collection = db['chat']


def load_messages(user_id):
    messages = messages_collection.find({'user_id': int(user_id)})
    response = [{'message': msg['message'], 'sender': msg['sender']} for msg in messages]
    print(response)


def scollect_user_responses(user_id):
    # Fetch messages for the specific user, sorting by _id to get the latest ones (or another timestamp field if available)
    user_messages = list(
        messages_collection.find({'user_id': user_id}).sort('_id', -1))  # Ensure you are sorting correctly

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
    paired_responses = []

    # Pair up the last 6 questions and answers
    for i in range(
            min(len(bot_questions), len(user_responses))):  # Only pair up to the available questions and responses
        paired_responses.append(f"{bot_questions[i]}: {user_responses[i]}")

    # Return only the last 6 paired responses
    return paired_responses[-6:]  # Return the last 6 pairs

def collect_user_responses(user_id):
    user_messages = messages_collection.find({'user_id': user_id, 'sender': 'user'}).sort('_id', -1).limit(3)
    user_responses = [msg['message'] for msg in user_messages]  # Collect only user messages
    return " , ".join(user_responses)  # Combine responses into a single prompt
user_id = 1111
print(scollect_user_responses(user_id))


