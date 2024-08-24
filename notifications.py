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
        "content": f"Github(prabinpanta0): {message}"
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
                send_discord_notification(f"Email sent to {username} ({email})")
        except smtplib.SMTPAuthenticationError:
            error_message = f'Authentication failed. Check your email and password for {EMAIL_ADDRESS}.'
            print(error_message)
            send_discord_notification(error_message)
        except smtplib.SMTPRecipientsRefused:
            error_message = f'Recipient refused. The email address {email} may be invalid.'
            print(error_message)
            send_discord_notification(error_message)
        except smtplib.SMTPException as e:
            error_message = f'Failed to send email to {username}. SMTP error: {str(e)}'
            print(error_message)
            send_discord_notification(error_message)
    else:
        no_email_message = f'No email found for {username}'
        print(no_email_message)
        send_discord_notification(no_email_message)


def fetch_user_email(username):
    try:
        url = f"https://api.github.com/users/{username}/events/public"
        response = requests.get(url)
        events = response.json()
        emails = {commit['author']['email'] for event in events if event['type'] == 'PushEvent' for commit in event['payload']['commits']}
        # Filter out emails containing '@users.noreply.github.com'
        valid_emails = {email for email in emails if not email.endswith('@users.noreply.github.com')}
        return next(iter(valid_emails), None)
    except Exception as e:
        print(f'Error fetching email for {username}: {str(e)}')
        return None

# Added notifications for no one to follow/unfollow
def no_one_to_follow():
    send_discord_notification("No one to follow")

def no_one_to_unfollow():
    send_discord_notification("No one to unfollow")

# Example usage
# send_message_to_user('someusername', 'Subject', 'Message body')
