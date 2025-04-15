import os
import psycopg2
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
from twilio.rest import Client

app = Flask(__name__)
CORS(app)

# PostgreSQL DB config using environment variables
db = psycopg2.connect(
    host=os.environ.get("DB_HOST"),
    database=os.environ.get("DB_NAME"),
    user=os.environ.get("DB_USER"),
    password=os.environ.get("DB_PASSWORD")
)
cursor = db.cursor()

# ✅ Twilio (keep your current code here)
account_sid = os.environ.get("TWILIO_SID")
auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
twilio_number = os.environ.get("TWILIO_NUMBER")

client = Client(account_sid, auth_token)

@app.route('/submit-order', methods=['POST'])
def submit_order():
    data = request.json
    name = data['name']
    phone = data['phone']
    seat = data['seat']
    items_ordered = data['items']
    total = data['amount']
    status = data['payment_status']
    time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    query = """
    INSERT INTO orders (customer_name, phone_number, seat_number, items_ordered, total_amount, payment_status, order_time)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(query, (name, phone, seat, items_ordered, total, status, time))
    db.commit()

    try:
        message_body = f"Hi {name}, thank you for your order at Pixel Plates! 🍽️\nItems: {items_ordered}\nTotal: ₹{total}\nSeat: {seat}"
        client.messages.create(
            body=message_body,
            from_=twilio_number,
            to=f'+91{phone}'
        )
    except Exception as e:
        print("Error sending SMS:", e)

    return jsonify({'message': 'Order stored successfully!'})

if __name__ == '__main__':
    app.run(debug=True)
