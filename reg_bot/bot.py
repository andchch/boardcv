import os
import sqlite3
import logging
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import filters, ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler

# Configure logging
logging.basicConfig(
    filename='bot.log',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)


def db_init() -> sqlite3.Connection:
    """
    Initializes the database connection.

    Returns:
        sqlite3.Connection: A connection object to the SQLite database.
    """
    if not os.path.exists('db'):
        os.mkdir('db')
    connection = sqlite3.connect('db/users.db')
    cursor = connection.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
        user_id INTEGER PRIMARY KEY,
        username TEXT NOT NULL
        )
        ''')

    connection.commit()
    return connection


def db_add_user(update: Update) -> None:
    """
    Adds or updates a user in the database.

    Parameters:
        update (telegram.Update): The Telegram update object containing user information.
    """
    db = db_init()
    user_id = update.effective_user.id
    username = update.effective_user.username
    cursor = db.cursor()
    cursor.execute('SELECT * FROM Users WHERE user_id=?', (user_id,))
    user = cursor.fetchone()

    if user:
        logging.info(f'User {username} with ID {user_id} already exists.')
    else:
        cursor.execute('INSERT INTO Users (user_id, username) VALUES (?, ?)', (user_id, username))
        db.commit()
        logging.info(f'User {username} with ID {user_id} added successfully.')

    db.close()


def db_delete_user(update: Update) -> None:
    """
    Deletes a user from the database.

    Parameters:
        update (telegram.Update): The Telegram update object containing user information.
    """
    db = db_init()
    user_id = update.effective_user.id
    username = update.effective_user.username
    cursor = db.cursor()
    cursor.execute('SELECT * FROM Users WHERE user_id=?', (user_id,))
    user = cursor.fetchone()

    if user:
        cursor.execute('DELETE FROM Users WHERE user_id=?', (user_id,))
        db.commit()
        logging.info(f'User {username} with ID {user_id} deleted successfully.')
    else:
        logging.info(f'User {username} with ID {user_id} does not exist in database.')

    db.close()


# Handler for the /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db_add_user(update)
    # Create keyboard with options
    keyboard = [
        [
            '/update',
            '/delete'
        ]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=False)

    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text='Вы успешно зарегистрировались.')
    await update.message.reply_text('Выберите действие:', reply_markup=reply_markup)


# Handler for the /update command (updates user information)
async def user_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db_add_user(update)
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text='Ваша запись обновлена.')


# Handler for the /delete command (deletes user information)
async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db_delete_user(update)
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text='Ваша запись удалена.')


# Handler for unknown commands
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text='Команда не распознана.')


if __name__ == '__main__':
    dotenv_path = '/app/cfg/.env'
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)
        logging.info('.env loaded successfully.')
    else:
        logging.warning('No .env file found')

    # Create the Telegram bot application
    application = ApplicationBuilder().token(os.getenv('TELEGRAM_BOT_TOKEN')).build()

    # Add command handlers
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    delete_handler = CommandHandler('delete', delete)
    application.add_handler(delete_handler)

    update_handler = CommandHandler('update', user_update)
    application.add_handler(update_handler)

    unknown_handler = MessageHandler(filters.COMMAND, unknown)
    application.add_handler(unknown_handler)

    # Start the bot in polling mode
    application.run_polling()
