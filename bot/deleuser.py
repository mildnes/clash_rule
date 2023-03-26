import requests
import json
import datetime
import os

import telegram
from telegram.ext import Updater, CommandHandler

# Emby API settings
EMBY_API_URL = "http://10.10.10.122:8096/emby"
EMBY_ACCESS_TOKEN = "db0cdfb001124a5ab5d1da47377c03a3"

# Telegram Bot settings
TELEGRAM_BOT_TOKEN = "6216497652:AAGdvrJtMT71IaHHhC6TBmJRLSd6nwrU3fY"
TELEGRAM_CHAT_ID = "224910203"

# Calculate the date 30 days ago from today.
THIRTY_DAYS_AGO = (datetime.datetime.now() - datetime.timedelta(days=30)).strftime("%Y-%m-%d")

# Initialize Telegram Bot
bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)


def delete_inactive_users(update, context):
    # Send a message to the Telegram chat to indicate that the bot is working.
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text="开始清理用户...")

    # Send an API request to get the list of users.
    headers = {"X-Emby-Token": EMBY_ACCESS_TOKEN}
    users_api_url = EMBY_API_URL + "/Users"
    response = requests.get(users_api_url, headers=headers)
    users = json.loads(response.text)

    # Initialize count of deleted users to 0
    deleted_user_count = 0

    # Loop through each user and check if they have been inactive for 30 days or more.
    for user in users:
        last_login_date = user.get("LastLoginDate")
        if last_login_date is None:
            # If the user has never logged in, assume they are inactive.
            last_login_date = "1900-01-01"
        if last_login_date < THIRTY_DAYS_AGO:
            # If the user has not logged in for 30 days or more, delete their account.
            user_id = user.get("Id")
            delete_user_api_url = EMBY_API_URL + f"/Users/{user_id}"
            response = requests.delete(delete_user_api_url, headers=headers)
            deleted_user_count += 1
            bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=f"Deleted user {user.get('Name')} (id: {user_id})")

    # Send a message to the Telegram chat to indicate that the bot has finished working and the number of deleted users.
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=f"已完成不活跃用户的检查，总计删除了{deleted_user_count}个用户")


# Initialize the Telegram Bot updater and add the command handler for /delete_user
updater = Updater(token=TELEGRAM_BOT_TOKEN, use_context=True)
updater.dispatcher.add_handler(CommandHandler("delete_user", delete_inactive_users))

# Start the Telegram Bot
updater.start_polling()
updater.idle()