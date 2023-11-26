from flask import Flask, render_template, request
from datetime import datetime, timedelta
import pandas as pd
from infobip_channels.sms.channel import SMSChannel

app = Flask(__name__)
user_data = {}

# Infobip API credentials and recipient number
BASE_URL = "https://l3xwd2.api.infobip.com"
API_KEY = "1ba151de4fe6dcdcee61261cdfa0c5f8-93fa434f-9d4c-4138-b356-e2577d0494e6"

import os 
API_KEY = os.environ.get("1ba151de4fe6dcdcee61261cdfa0c5f8-93fa434f-9d4c-4138-b356-e2577d0494e6")

if API_KEY is None:
    raise ValueError("Infobip API key not found. Set INFOBIP_API_KEY environment variable.")

# Initialize the SMS channel with your Infobip credentials
channel = SMSChannel.from_auth_params({"base_url": BASE_URL, "api_key": API_KEY})

# Load the dataset
dataset_path = 'cycle_data.csv'  # Update this path accordingly
dataset = pd.read_csv(dataset_path, sep=';')

@app.route('/')

def index():
    return render_template('index.html')

def parse_date(date_str):
    try:
        return datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        return None

@app.route('/predict', methods=['POST'])
def predict():
    username = request.form['username']
    date1 = parse_date(request.form['date1'])
    date2 = parse_date(request.form['date2'])
    weight = request.form['weight']
    age = request.form['age']
    recipient_number = request.form['recipient_number']

    if None in (date1, date2):
        return "Invalid date format. Please use YYYY-MM-DD."

    try:
        weight = float(weight)
        age = int(age)
        if weight < 0 or age < 0:
            return "Weight and age cannot be negative."
    except ValueError:
        return "Invalid input for weight or age. Please enter valid numbers."

    # Calculate the difference between dates
    date_difference = abs((date1 - date2).days)

    # Find average cycle length from the dataset for similar age and weight
    similar_users = dataset[(dataset['Age'] == age) & (dataset['Weight'] == weight)]
    if not similar_users.empty:
        average_cycle_length = similar_users['Difference'].mean()
    else:
        average_cycle_length = 28  # Default value if no similar users found

    # Predict the next period date using average cycle length
    last_period_date = max(date1, date2)
    predicted_next_period = last_period_date + timedelta(days=average_cycle_length)

    # Sending an SMS using Infobip API
    try:
        sms_response = channel.send_sms_message({
            "messages": [{
                "destinations": [{"to": recipient_number}],
                "text": f"Hello {username}! Your predicted next period date is {predicted_next_period.date()}."
            }]
        })

        print("SMS sent successfully!")
    except Exception as e:
        error_message = f"Error sending SMS: {str(e)}"
        print(error_message)
        return render_template('error.html', error_message=error_message)

    return render_template('result.html', username=username, predicted_date=predicted_next_period.date())

if __name__ == '__main__':
    app.run(debug=True)
    