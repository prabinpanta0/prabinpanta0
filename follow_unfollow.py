import os
import requests
import time
from notifications import send_message_to_user, send_discord_notification, no_one_to_follow, no_one_to_unfollow

# Get environment variables
GITHUB_TOKEN = os.getenv('TOKEN')
GITHUB_USERNAME = os.getenv('USERNAME')

headers = {'Authorization': f'token {GITHUB_TOKEN}'}

def get_following():
    following = []
    page = 1
    while True:
        url = f'https://api.github.com/users/{GITHUB_USERNAME}/following?per_page=100&page={page}'
        response = requests.get(url, headers=headers)
        data = response.json()
        if not data:
            break
        following.extend([user['login'] for user in data])
        page += 1
    return following

def get_followers():
    followers = []
    page = 1
    while True:
        url = f'https://api.github.com/users/{GITHUB_USERNAME}/followers?per_page=110&page={page}'
        response = requests.get(url, headers=headers)
        data = response.json()
        if not data:
            break
        followers.extend([user['login'] for user in data])
        page += 1
    return followers

def follow_user(user, retries=3):
    follow_url = f'https://api.github.com/user/following/{user}'
    for attempt in range(retries):
        response = requests.put(follow_url, headers=headers)
        if response.status_code == 204:
            return True
        elif response.status_code == 403:
            print(f'Rate limit hit. Waiting before retrying...')
            time.sleep(60)
        else:
            time.sleep(2)
    return False

def follow_all_followers():
    following = set(get_following())
    followers = set(get_followers())
    non_following = list(followers - following)
    if not non_following:
        print('No one Left to follow back')
        no_one_to_follow()
        return
    print(f'\n {len(non_following)} are left to followback \n')
    print('\nList of non-followers:\n')
    for i, user in enumerate(non_following, 1):
        if follow_user(user):
            print(f'{i}. followed {user}.')
            send_message_to_user(user, f"Dear {user}, Thank you for following!", f"It's great to have you on board. {GITHUB_USERNAME} (GitHub)")
            send_discord_notification(f"Followed {user}.")
        else:
            print(f'{i}. Failed to follow {user}.')
            send_discord_notification(f"Failed to follow {user}.")
        time.sleep(2)
    print('\nFinished processing all non-following.')

follow_all_followers()

def unfollow_user(user, retries=3):
    unfollow_url = f'https://api.github.com/user/following/{user}'
    for attempt in range(retries):
        response = requests.delete(unfollow_url, headers=headers)
        if response.status_code == 204:
            return True
        elif response.status_code == 403:
            print(f'Rate limit hit. Waiting before retrying...')
            time.sleep(60)
        else:
            time.sleep(2)
    return False

def find_and_unfollow_non_followers():
    following = set(get_following())
    followers = set(get_followers())
    non_followers = list(following - followers)
    if not non_followers:
        print('You don\'t follow anyone who doesn\'t follow you back.')
        no_one_to_unfollow()
        return
    print(f'\nYou follow {len(non_followers)} people who don\'t follow you back.')
    print('\nList of non-followers:\n')
    for i, user in enumerate(non_followers, 1):
        if unfollow_user(user):
            print(f'{i}. Unfollowed {user}.')
            send_message_to_user(user, f"Dear {user}, It's sad to see you go", f"We hope to see you again! {GITHUB_USERNAME} (GitHub)")
            send_discord_notification(f"Unfollowed {user}.")
        else:
            print(f'{i}. Failed to unfollow {user}.')
            send_discord_notification(f"Failed to unfollow {user}.")
        time.sleep(2)
    print('\nFinished processing all non-followers.')

find_and_unfollow_non_followers()
