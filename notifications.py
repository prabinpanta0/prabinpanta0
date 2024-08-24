import requests
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')  # Your email address
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')  # Your email password

def send_discord_notification(message):
    data = {
        "content": message
    }
    response = requests.post(DISCORD_WEBHOOK_URL, json=data)
    if response.status_code != 204:
        raise Exception(f"Failed to send Discord notification: {response.status_code}, {response.text}")

def get_user_email(username):
    url = f"https://api.github.com/users/{username}/events/public"
    response = requests.get(url)
    if response.status_code == 200:
        events = response.json()
        emails = set()

        for event in events:
            if event['type'] == 'PushEvent':
                commits = event['payload'].get('commits', [])
                for commit in commits:
                    email = commit['author'].get('email')
                    if email:
                        emails.add(email)

        return list(emails)
    return []

def send_email(to_email, subject, body):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    text = msg.as_string()
    server.sendmail(EMAIL_ADDRESS, to_email, text)
    server.quit()

def send_message_to_user(username, action):
    emails = get_user_email(username)

    if not emails:
        no_email_message = f"No email found for {username}."
        print(no_email_message)
        send_discord_notification(no_email_message)  # Send Discord notification
        return

    for email in emails:
        if action == "follow":
            subject = "Thank You for Following!"
            body = f"Dear {username},\n\nThank you for following me on GitHub! I appreciate your support."
        elif action == "unfollow":
            subject = "Sad to See You Go"
            body = f"Dear {username},\n\nIt's sad to see you go. If you ever wish to reconnect, I'm here."
        else:
            subject = "Hello!"
            body = f"Dear {username},\n\nThank you for your interaction!"

        send_email(email, subject, body)
