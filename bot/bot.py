import os
import sqlite3
import telebot
import json
import subprocess
from dotenv import load_dotenv
from threading import local
from PIL import Image
from io import BytesIO
from threading import Thread
import sqlite3

conn = sqlite3.connect('miftah.db')
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS whitelist (
    user_id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    confirm_attempts INTEGER DEFAULT 0
)
''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS blacklist (
    user_id INTEGER PRIMARY KEY,
    username TEXT NOT NULL
)
''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS locked_users (
    user_id INTEGER PRIMARY KEY,
    password TEXT,
    token TEXT
)
''')
conn.commit()
conn.close()

# Load environment variables from .env file
load_dotenv()

# Load bot token and admin ID from environment variables
bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
admin_id = int(os.getenv('ADMIN_ID'))  # Ensure ADMIN_ID is set as an integer
bot = telebot.TeleBot(bot_token)

# Thread-local storage for database connections
thread_local = local()

def get_db_connection(db_name):
    if not hasattr(thread_local, db_name):
        conn = sqlite3.connect(f'{db_name}.db', check_same_thread=False)
        conn.execute('PRAGMA foreign_keys = ON')
        cursor = conn.cursor()
        setattr(thread_local, db_name, (conn, cursor))
    return getattr(thread_local, db_name)

class UserManager:
    def __init__(self):
        self.init_db()

    def init_db(self):
        conn, cursor = get_db_connection('users')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS whitelist (
            user_id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            confirm_attempts INTEGER DEFAULT 0
        )
        ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS blacklist (
            user_id INTEGER PRIMARY KEY,
            username TEXT NOT NULL
        )
        ''')
        conn.commit()
        
    def __init__miftah(self, user_id):
        self.db_connection = get_db_connection('miftah')
        self.user_id = user_id

    def is_locked(self):
        cursor = self.db_connection[1]
        cursor.execute("SELECT 1 FROM locked_users WHERE user_id = ?", (self.user_id,))
        return cursor.fetchone() is not None

    def lock_user(self, password, token):
        cursor = self.db_connection[1]
        cursor.execute("INSERT OR IGNORE INTO locked_users (user_id, password, token) VALUES (?, ?, ?)", (self.user_id, password, token))
        self.db_connection[0].commit()

    def unlock_user(self):
        cursor = self.db_connection[1]
        cursor.execute("DELETE FROM locked_users WHERE user_id = ?", (self.user_id,))
        self.db_connection[0].commit()

    def get_token(self):
        cursor = self.db_connection[1]
        cursor.execute("SELECT token FROM locked_users WHERE user_id = ?", (self.user_id,))
        result = cursor.fetchone()
        return result[0] if result else None

    def get_password(self):
        cursor = self.db_connection[1]
        cursor.execute("SELECT password FROM locked_users WHERE user_id = ?", (self.user_id,))
        result = cursor.fetchone()
        return result[0] if result else None

    def is_whitelisted(self, user_id):
        conn, cursor = get_db_connection('users')
        cursor.execute("SELECT 1 FROM whitelist WHERE user_id = ?", (user_id,))
        return cursor.fetchone() is not None

    def is_blacklisted(self, user_id):
        conn, cursor = get_db_connection('users')
        cursor.execute("SELECT 1 FROM blacklist WHERE user_id = ?", (user_id,))
        return cursor.fetchone() is not None

    def whitelist_user(self, user_id, username):
        conn, cursor = get_db_connection('users')
        cursor.execute("INSERT OR IGNORE INTO whitelist (user_id, username) VALUES (?, ?)", (user_id, username))
        conn.commit()

    def blacklist_user(self, user_id, username):
        conn, cursor = get_db_connection('users')
        cursor.execute("INSERT OR IGNORE INTO blacklist (user_id, username) VALUES (?, ?)", (user_id, username))
        conn.commit()

    def increment_confirm_attempts(self, user_id):
        conn, cursor = get_db_connection('users')
        cursor.execute("UPDATE whitelist SET confirm_attempts = confirm_attempts + 1 WHERE user_id = ?", (user_id,))
        conn.commit()

    def get_confirm_attempts(self, user_id):
        conn, cursor = get_db_connection('users')
        cursor.execute("SELECT confirm_attempts FROM whitelist WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        return result[0] if result else 0

user_manager = UserManager()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    if user_manager.is_whitelisted(user_id):
        welcome_text = (
            "Welcome to the SSH Reseller Bot!\n\n"
            "Here are the commands you can use:\n"
            "/contohmenuinfo - Description of contohmenuinfo\n"
            "/grpcmenu - Description of grpcmenu\n"
            "/grpcmenu2 - Description of grpcmenu2\n"
            "/grpcupdate - Description of grpcupdate\n"
            "/grpcupdate2 - Description of grpcupdate2\n"
            "/ipsaya - Description of ipsaya\n"
            "/l2tpmenu - Description of l2tpmenu\n"
            "/menu - Description of menu\n"
            "/menuinfo - Description of menuinfo\n"
            "/pptpmenu - Description of pptpmenu\n"
            "/running - Description of running\n"
            "/setmenu - Description of setmenu\n"
            "/slowdnsmenu - Description of slowdnsmenu\n"
            "/sshovpn - Description of sshovpn\n"
            "/ssmenu - Description of ssmenu\n"
            "/ssrmenu - Description of ssrmenu\n"
            "/sstpmenu - Description of sstpmenu\n"
            "/trgomenu - Description of trgomenu\n"
            "/trmenu - Description of trmenu\n"
            "/updatemenu - Description of updatemenu\n"
            "/vlessmenu - Description of vlessmenu\n"
            "/vmessmenu - Description of vmessmenu\n"
            "/wgmenu - Description of wgmenu\n"
        )
        bot.reply_to(message, welcome_text)
    else:
        bot.reply_to(message, "You are not whitelisted. Please register with /register.")

@bot.message_handler(commands=['register'])
def register_user(message):
    user_id = message.from_user.id
    username = message.from_user.username
    if not username:
        bot.reply_to(message, "Please set a username in your Telegram account.")
        return

    user_manager.whitelist_user(user_id, username)
    bot.reply_to(message, "You have been registered. Please wait for admin confirmation.")

@bot.message_handler(commands=['confirm'])
def confirm_user(message):
    user_id = message.from_user.id
    if user_id == admin_id:
        try:
            token = message.text.split('/confirm ', 1)[1].strip()
            # Logic to find and confirm user by token
            # ...
            bot.reply_to(message, "User confirmed successfully.")
        except Exception as e:
            bot.reply_to(message, f"Error confirming user: {str(e)}")
    else:
        user_manager.increment_confirm_attempts(user_id)
        attempts = user_manager.get_confirm_attempts(user_id)
        if attempts > 3:
            user_manager.blacklist_user(user_id, message.from_user.username)
            bot.reply_to(message, "You have been blacklisted for spamming.")
        else:
            bot.reply_to(message, "You are not authorized to confirm users.")

@bot.message_handler(commands=[
    'contohmenuinfo', 'grpcmenu', 'grpcmenu2', 'grpcupdate', 'grpcupdate2',
    'ipsaya', 'l2tpmenu', 'menu', 'menuinfo', 'pptpmenu', 'running', 
    'setmenu', 'slowdnsmenu', 'sshovpn', 'ssmenu', 'ssrmenu', 'sstpmenu', 
    'trgomenu', 'trmenu', 'updatemenu', 'vlessmenu', 'vmessmenu', 'wgmenu'])
def handle_commands(message):
    user_id = message.from_user.id
    if user_manager.is_blacklisted(user_id):
        bot.reply_to(message, "You are blacklisted and cannot use this bot.")
        return

    if user_manager.is_whitelisted(user_id):
        command = message.text.lstrip('/')
        output = run_system_command(command)
        bot.reply_to(message, f"Output of {command}:\n{output}")
    else:
        bot.reply_to(message, "You are not authorized to use this bot. Please register first.")

def run_system_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = result.stdout.decode('utf-8').strip()
        return f"```{output}```"
    except subprocess.CalledProcessError as e:
        error_output = e.stderr.decode('utf-8').strip()
        return f"Error executing command:\n```{error_output}```"

@bot.message_handler(func=lambda message: True)
def fallback_handler(message):
    bot.reply_to(message, "Unrecognized command. Please use a valid command.")

# Start bot
bot.polling()
