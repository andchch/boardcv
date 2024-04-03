import os
import sqlite3
import telegram
from telegram.error import BadRequest


def db_init():
    connection = sqlite3.connect(os.getenv('DATABASE_PATH', default='users.db'))
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
    db = db_init()
    cursor = db.cursor()
    cursor.execute('SELECT user_id, username FROM Users WHERE username = ?', (username,))
    users = cursor.fetchall()
    db.close()
    if not users:
        return None
    else:
        return users[0][0]


async def send_message(username: str, message: str):
    bot = telegram.Bot(os.getenv('TELEGRAM_BOT_TOKEN'))
    chat_id = get_user_id(username)
    await bot.send_message(chat_id=chat_id, text=message)

if __name__ == '__main__':
    a = get_user_id('andchcf')
    print(a)
