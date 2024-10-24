from pymongo import MongoClient

from pymongo.server_api import ServerApi


uri = ""
client = MongoClient(uri, server_api=ServerApi('1'))
db = client['test']
messages_collection = db['chat']

results = []


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
    results = []  # Initialize the list to hold the results

    for i in range(6):
        # Find the last bot message
        last_entry_bot = messages_collection.find({'user_id': user_id, "sender": "bot"}).sort('_id', -1).skip(i).limit(
            1)
        bot_message = None
        if last_entry_bot:  # Ensure there's at least one message
            bot_message = last_entry_bot[0].get("message")

        # Find the last user message
        last_entry_user = messages_collection.find({'user_id': user_id, "sender": "user"}).sort('_id', -1).skip(
            i).limit(1)
        user_message = None
        if last_entry_user:
            user_message = last_entry_user[0].get("message")

        # Append the paired message to results if both exist
        if bot_message and user_message:
            results.append(f"{bot_message}: {user_message}")

    return results


# Example usage
user_id = 1111
last_entry = get_last_entry(user_id)

qa_dict = extract_question_answers(last_entry)
print(qa_dict.get("What career do you dream of pursuing after high school?"))
