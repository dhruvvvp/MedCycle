from flask import Flask, render_template, request
from datetime import datetime, timedelta
from infobip_channels.sms.channel import SMSChannel

app = Flask(__name__)
user_data = {}

# Infobip API credentials and recipient number
BASE_URL = "https://l3xwd2.api.infobip.com"
API_KEY = "1ba151de4fe6dcdcee61261cdfa0c5f8-93fa434f-9d4c-4138-b356-e2577d0494e6"


# Initialize the SMS channel with your Infobip credentials
channel = SMSChannel.from_auth_params({"base_url": BASE_URL, "api_key": API_KEY})

def predict_next_period(username):
    if username in user_data and len(user_data[username]) >= 2:
        period_dates = sorted(user_data[username])
        cycle_lengths = [period_dates[i] - period_dates[i - 1] for i in range(1, len(period_dates))]
        average_cycle_length = sum(cycle_lengths, timedelta()) // len(cycle_lengths)
        last_period_date = period_dates[-1]
        predicted_next_period = last_period_date + average_cycle_length
        return predicted_next_period.date()
    return None

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

    if None in (date1, date2):
        return "Invalid date format. Please use YYYY-MM-DD."


    try:
        weight = float(weight)
        age = int(age)
        if weight < 0:
            return "Weight cannot be negative."

        if age < 0:
            return "Age cannot be negative."

        if age >= 55:
            return "Your next period will not happen since your menstrual cycle has ended."

    except ValueError:
        return "Invalid input for weight or age. Please enter valid numbers."

    user_data.setdefault(username, []).extend([date1, date2])

    predicted_date = predict_next_period(username)
    if predicted_date:
        return render_template('result.html', username=username, predicted_date=predicted_date)
    else:
        return render_template('result.html', username=username, predicted_date="Not available or error occurred")
    # Calculate average cycle length (assuming 28 days)

# Send SMS function
@app.route('/sendsms', methods=['POST'])
def send_sms_from_button():
    username = request.form['username']
    recipient_number = request.form['recipient_number']
    predicted_date = request.form['predicted_date']  # Retrieve the predicted_date

    try:
        sms_response = channel.send_sms_message({
            "messages": [{
                "destinations": [{"to": recipient_number}],
                "text": f"Hello {username}! Your predicted next period date is {predicted_date}."
            }]
        })

        print("SMS sent successfully!")
    except Exception as e:
        print(f"Error sending SMS: {str(e)}")

    return "SMS Sent!"

if __name__ == '__main__':
    app.run(debug=True)
