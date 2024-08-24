import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests

DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

def send_discord_notification(message):
    data = {
        "content": message
    }
    response = requests.post(DISCORD_WEBHOOK_URL, json=data)
    if response.status_code != 204:
        print(f"Failed to send Discord notification. Status code: {response.status_code}")

def send_message_to_user(username, subject, body):
    # Fetch the user's email
    email = fetch_user_email(username)
    
    if email:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                server.sendmail(EMAIL_ADDRESS, email, msg.as_string())
                print(f'Email sent to {username} ({email})')
        except Exception as e:
            print(f'Failed to send email to {username}. Error: {str(e)}')
            send_discord_notification(f"Failed to send email to {username} ({email}).")
    else:
        print(f'No email found for {username}')
        send_discord_notification(f'No email found for {username}')

def fetch_user_email(username):
    try:
        url = f"https://api.github.com/users/{username}/events/public"
        response = requests.get(url)
        events = response.json()
        emails = {commit['author']['email'] for event in events if event['type'] == 'PushEvent' for commit in event['payload']['commits']}
        return next(iter(emails), None)
    except Exception as e:
        print(f'Error fetching email for {username}: {str(e)}')
        return None
