import telebot
import sqlite3
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Load bot token and admin ID from environment variables
bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
admin_id = os.getenv('ADMIN_ID')  # ensure ADMIN_ID is set as an integer
bot = telebot.TeleBot(bot_token)

# Database connections
conn = sqlite3.connect('miftah.db')
cursor = conn.cursor()

# Ensure necessary tables exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    token TEXT NOT NULL,
    locked INTEGER DEFAULT 1
)
''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS whitelist (
    user_id INTEGER PRIMARY KEY,
    username TEXT NOT NULL
)
''')
conn.commit()

# Command handlers
@bot.message_handler(commands=['contohmenuinfo', 'grpcmenu', 'grpcmenu2', 'grpcupdate', 'grpcupdate2',
                               'ipsaya', 'l2tpmenu', 'menu', 'menuinfo', 'pptpmenu', 'running', 
                               'setmenu', 'slowdnsmenu', 'sshovpn', 'ssmenu', 'ssrmenu', 'sstpmenu', 
                               'trgomenu', 'trmenu', 'updatemenu', 'vlessmenu', 'vmessmenu', 'wgmenu'])
def handle_commands(message):
    command = message.text.lstrip('/')
    if user_is_whitelisted(message.from_user.id):
        output = run_system_command(command)
        bot.reply_to(message, f"Output of {command}:\n{output}")
    else:
        bot.reply_to(message, "You are not authorized to use this bot. Please register first.")

def run_system_command(command):
    import subprocess
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.stdout.decode('utf-8')
    except subprocess.CalledProcessError as e:
        return f"Error executing command:\n{e.stderr.decode('utf-8')}"

def user_is_whitelisted(user_id):
    cursor.execute("SELECT 1 FROM whitelist WHERE user_id = ?", (user_id,))
    return cursor.fetchone() is not None

# Registration process
@bot.message_handler(commands=['register'])
def register_user(message):
    user_id = message.from_user.id
    username = message.from_user.username
    token = generate_token(user_id)
    cursor.execute("INSERT INTO users (user_id, username, password, token) VALUES (?, ?, ?, ?)",
                   (user_id, username, '', token))
    conn.commit()
    bot.reply_to(message, f"Please complete registration by scanning the QR code and confirming with admin.\nToken: {token}")

def generate_token(user_id):
    import uuid
    return str(uuid.uuid4())

@bot.message_handler(commands=['confirm'])
def confirm_user(message):
    if message.from_user.id == admin_id:
        try:
            data = json.loads(message.text.lstrip('/confirm '))
            user_id = data['user_id']
            password = data['password']
            cursor.execute("UPDATE users SET password = ?, locked = 0 WHERE user_id = ?", (password, user_id))
            cursor.execute("INSERT INTO whitelist (user_id, username) SELECT user_id, username FROM users WHERE user_id = ?", (user_id,))
            conn.commit()
            bot.reply_to(message, "User confirmed successfully.")
        except Exception as e:
            bot.reply_to(message, f"Error confirming user: {str(e)}")
    else:
        bot.reply_to(message, "You are not authorized to confirm users.")

@bot.message_handler(func=lambda message: True)
def fallback_handler(message):
    bot.reply_to(message, "Unrecognized command. Please use a valid command.")

# Error handling
@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_errors(message):
    bot.reply_to(message, "Something went wrong. Please try again later.")

# Start bot
bot.polling()
