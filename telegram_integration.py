import os
import sqlite3
import telegram
from dotenv import load_dotenv
from telegram.error import BadRequest

dotenv_path = 'cfg/.env'
load_dotenv(dotenv_path)


def db_init() -> sqlite3.Connection:
    """
    Initializes the database connection.

    Returns:
        sqlite3.Connection: A connection object to the SQLite database.
    """
    connection = sqlite3.connect(os.getenv('DATABASE_PATH', default='db/users.db'))
    cursor = connection.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
        user_id INTEGER PRIMARY KEY,
        username TEXT NOT NULL
        )
        ''')

    connection.commit()
    return connection


async def check_usernames():
    """
    Checks and updates usernames in the database to ensure they are current.

    This function iterates through all users in the database and retrieves their
    current usernames from Telegram. If the stored username doesn't match the actual
    username, it updates the database with the correct username.

    Prints a message indicating whether any usernames were updated or if all
    usernames were already correct.
    """
    bot = telegram.Bot(os.getenv('TELEGRAM_BOT_TOKEN'))

    fixed = False
    db = db_init()
    cursor = db.cursor()
    cursor.execute('SELECT user_id, username FROM Users')
    users = cursor.fetchall()

    for user_id, username in users:
        try:
            chat = await bot.get_chat(chat_id=user_id)
            expected_username = chat.username
        except BadRequest:
            pass

        if username != expected_username and expected_username is not None:
            print(f'Incorrect username for user with ID {user_id}: {username} (expected: {expected_username})')
            cursor.execute('UPDATE Users SET username=? WHERE user_id=?', (expected_username, user_id))
            db.commit()
            fixed = True
    if not fixed:
        print('Success. No username changes were made.')
    db.close()


def get_user_id(username: str) -> int | None:
    """
    Retrieves the user ID associated with a given username.

    Parameters:
        username (str): The username to search for.

    Returns:
        int | None: The user ID if found, otherwise None.
    """
    db = db_init()
    cursor = db.cursor()
    cursor.execute('SELECT user_id, username FROM Users WHERE username = ?', (username,))
    users = cursor.fetchall()
    db.close()
    if not users:
        return None
    else:
        return users[0][0]


async def send_message(username: str, message: str, img=None):
    """
    Sends a message to a user with an optional image attachment.

    Parameters:
        username (str): The username of the recipient.
        message (str): The message text to send.
        img (str | None, optional): The path to the image file to attach. Defaults to None.
    """
    bot = telegram.Bot(os.getenv('TELEGRAM_BOT_TOKEN'))
    chat_id = get_user_id(username)
    if img is not None:
        await bot.send_document(chat_id=chat_id, document=img)
        await bot.send_message(chat_id=chat_id, text=message)
    else:
        await bot.send_message(chat_id=chat_id, text=message)
