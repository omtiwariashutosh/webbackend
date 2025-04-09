from flask import Flask, request, jsonify, render_template
import mysql.connector
import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQLHOST"),
        user=os.getenv("MYSQLUSER"),
        password=os.getenv("MYSQLPASSWORD"),
        database=os.getenv("MYSQLDATABASE"),
        port=os.getenv("MYSQLPORT")
    )

@app.route('/submit-form', methods=['POST'])
def submit_form():
    data = request.json
    name = data['name']
    email = data['email']
    subject = data['subject']
    message = data['message']
    address = data['address']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO contacts (name, email, subject, message, address) VALUES (%s, %s, %s, %s, %s)",
                   (name, email, subject, message, address))
    conn.commit()
    cursor.close()
    conn.close()

    html = render_template("email_template.html", data=data)

    send_email(subject, html)

    return jsonify({"message": "Form submitted and email sent!"})

def send_email(subject, html_content):
    sender = os.getenv("EMAIL")
    password = os.getenv("EMAILPASS")
    receiver = os.getenv("RECEIVER_EMAIL")

    msg = MIMEText(html_content, 'html')
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = receiver

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(sender, password)
        server.send_message(msg)

if __name__ == '__main__':
    app.run(debug=True)
