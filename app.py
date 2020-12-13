#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=W0613, C0116
# type: ignore[union-attr]
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.

First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""
import logging
import os

import psycopg2
from pip._vendor import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext, CallbackQueryHandler, CommandHandler, Updater

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

PG_CONNECTION_STRING = 'postgres://qoylexgbjnwyir:281532ff341d44531ed6bfddaf729fe315de20fab2ad6409ef5a74554f747942@ec2-52-30-161-203.eu-west-1.compute.amazonaws.com:5432/djhv36l77a6tl'


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    keyboard = [
        [
            InlineKeyboardButton("Yes", callback_data='1'),
            InlineKeyboardButton("No", callback_data='2'),
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Do you want a PS5?!',
                              reply_markup=reply_markup)


def register(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""

    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()

    chat_id = update.effective_chat.id

    if query.data == '1':
        if chat_id and str(chat_id) not in get_telegram_users(context):
            register_to_telegram(context, chat_id)
        query.edit_message_text(text='Registered! (/cancel to stop)')
        save_users_to_db(context)
    else:
        query.edit_message_text(text="Go buy an Xbox then...")


def keep_app_alive(*a, **kw):
    requests.get("https://ps5-alert-bot.herokuapp.com/")


def register_to_telegram(update, id):
    update.job_queue.run_repeating(check, 30, context=id, name=str(id))
    update.job_queue.run_repeating(notify_user_still_looking, 7200, context=id, name=str(id))


def check(context: CallbackContext, **kw) -> None:
    try:
        """Echo the user message."""
        job = context.job

        p = requests.get("https://www.bug.co.il/brand/ps5/ps5/console/digital", timeout=10)
        if not "product-page-no-inventory" in str(p._content):
            context.bot.send_message(job.context, text='BUG! https://www.bug.co.il/brand/ps5/ps5/console/digital')
            print(f'Status Code: {p.status_code}, URL: {p.url}, Is Redirect: {p.is_redirect}')

        p = requests.get("https://www.bug.co.il/brand/ps5/ps5/console/blue/ray", timeout=10)
        if not "product-page-no-inventory" in str(p._content):
            context.bot.send_message(job.context, text='BUG! https://www.bug.co.il/brand/ps5/ps5/console/blue/ray')
            print(f'Status Code: {p.status_code}, URL: {p.url}, Is Redirect: {p.is_redirect}')

        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        p = requests.get("https://www.ivory.co.il/Sony_Playstation_5.html", allow_redirects=False, headers=headers,
                         timeout=10)
        if "m-area-prd" in str(p.content):
            context.bot.send_message(job.context, text="IVORYYY  https://www.ivory.co.il/Sony_Playstation_5.html")
            print(f'Status Code: {p.status_code}, URL: {p.url}, Is Redirect: {p.is_redirect}')

        url = "https://vgs.co.il/%D7%9E%D7%95%D7%A6%D7%A8/sony-ps5-console-%d7%a7%d7%95%d7%a0%d7%a1%d7%95%d7%9c%d7%aa-%d7%a4%d7%9c%d7%99%d7%99%d7%a1%d7%98%d7%99%d7%99%d7%a9%d7%9f-5-%d7%9e%d7%9b%d7%99%d7%a8%d7%94/"
        p = requests.get(url, allow_redirects=False, headers=headers, timeout=10)
        if "single_add_to_cart_button" in str(p.content):
            context.bot.send_message(job.context, text=f"VGSSSSS  {url}")
            print(f'Status Code: {p.status_code}, URL: {p.url}, Is Redirect: {p.is_redirect}')

        url = "https://vgs.co.il/%D7%9E%D7%95%D7%A6%D7%A8/sony-ps5-console-digital-edition-%d7%a7%d7%95%d7%a0%d7%a1%d7%95%d7%9c%d7%aa-%d7%a4%d7%9c%d7%99%d7%99%d7%a1%d7%98%d7%99%d7%99%d7%a9%d7%9f-5-%d7%9c%d7%9c%d7%90-%d7%9b%d7%95%d7%a0%d7%9f-%d7%93%d7%99/"
        p = requests.get(url, allow_redirects=False, headers=headers, timeout=10)
        if "single_add_to_cart_button" in str(p.content):
            context.bot.send_message(job.context, text=f"VGSSSSS  {url}")
            print(f'Status Code: {p.status_code}, URL: {p.url}, Is Redirect: {p.is_redirect}')

    except Exception as e:
        print(e)


def cancel(update: Update, context: CallbackContext) -> None:
    jobs = context.job_queue.get_jobs_by_name(str(update.message.chat_id))

    if jobs:
        for job in jobs:
            job.schedule_removal()

    if update.message.chat_id:
        remove_db_user(str(update.message.chat_id))

    update.message.reply_text("You won't know when a PS5 is out!")


def remove_db_user(id):
    with psycopg2.connect(PG_CONNECTION_STRING) as conn:
        try:
            cur = conn.cursor()
            cur.execute(f"DELETE FROM USER_IDS WHERE ID='{id}'")
            conn.commit()

        except Exception as e:
            print(e)


def get_db_users():
    with psycopg2.connect(PG_CONNECTION_STRING) as conn:
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM USER_IDS")
            rows = cur.fetchall()
            return [row[0] for row in rows]

        except Exception as e:
            print(e)


def save_users_to_db(context: CallbackContext):
    with psycopg2.connect(PG_CONNECTION_STRING) as conn:
        try:
            ids = get_telegram_users(context)

            cur = conn.cursor()
            all_ids = ','.join([f'(\'{dbid}\')' for dbid in ids])
            cur.execute(f"INSERT INTO USER_IDS VALUES {all_ids} ON CONFLICT DO NOTHING")
            conn.commit()

        except Exception as e:
            print(e)


def get_telegram_users(context):
    jobs = context.job_queue.jobs()
    ids = {j.context for j in jobs if j != 'KEEP_ALIVE' and j.context}
    return ids


def notify_user_still_looking(context: CallbackContext):
    context.bot.send_message(context.job.context, text="Didn't find a PS5 yet...")


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater("1418644151:AAGdaaRuZinX98D13u3uoyke6KVRvg0lh0U", use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    # dispatcher.add_handler(CommandHandler("start", start))
    # dispatcher.add_handler(CommandHandler("help", help_command))

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CallbackQueryHandler(register))
    updater.dispatcher.add_handler(CommandHandler('cancel', cancel))

    for id in get_db_users():
        register_to_telegram(updater, id)

    updater.job_queue.run_repeating(keep_app_alive, 600, name="KEEP_ALIVE")

    # on noncommand i.e message - echo the message on Telegram
    # dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Start the Bot
    # updater.start_polling()

    PORT = int(os.environ.get('PORT', 5000))
    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path='AAGdaaRuZinX98D13u3uoyke6KVRvg0lh0U')
    updater.bot.setWebhook('https://ps5-alert-bot.herokuapp.com/' + 'AAGdaaRuZinX98D13u3uoyke6KVRvg0lh0U')

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
