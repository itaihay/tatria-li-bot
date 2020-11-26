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

from pip._vendor import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

YES = 1


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

    if query.data == '1':
        context.job_queue.run_repeating(check, 120, context=update.effective_chat.id,
                                        name=str(update.effective_chat.id))
        query.edit_message_text(text='Registered! (/cancel to stop)')


def check(context: CallbackContext, **kw) -> None:
    """Echo the user message."""
    job = context.job

    p = requests.get("https://www.bug.co.il/brand/ps5/ps5/console/digital")
    if (p.status_code == 200) and (not "product-page-no-inventory" in str(p._content)):
        context.bot.send_message(job.context, text='BUG! https://www.bug.co.il/brand/ps5/ps5/console/digital')

    p = requests.get("https://www.bug.co.il/brand/ps5/ps5/console/blue/ray")
    if (p.status_code == 200) and (not "product-page-no-inventory" in str(p._content)):
        context.bot.send_message(job.context, text='BUG! https://www.bug.co.il/brand/ps5/ps5/console/blue/ray')

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    p = requests.get("https://www.ivory.co.il/Sony_Playstation_5.html", headers=headers)
    b = b'\xd7\x9e\xd7\x95\xd7\xa6\xd7\xa8 / \xd7\x93\xd7\xa3 \xd7\x96\xd7\x94 \xd7\x94\xd7\x95\xd7\xa1\xd7\xa8 \xd7\x9e\xd7\x90\xd7\xaa\xd7\xa8\xd7\xa0\xd7\x95'
    if (p.status_code == 200) and (not (b in p.content)):
        context.bot.send_message(job.context, text="IVORYYY  https://www.ivory.co.il/Sony_Playstation_5.html")


def cancel(update: Update, context: CallbackContext) -> None:
    jobs = context.job_queue.get_jobs_by_name(str(update.message.chat_id))

    if jobs:
        for job in jobs:
            job.schedule_removal()

    update.message.reply_text("You won't know when a PS5 is out!")


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

    # on noncommand i.e message - echo the message on Telegram
    # dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Start the Bot
    # updater.start_polling()
    PORT = int(os.environ.get('PORT', 5000))
    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path='1418644151')
    updater.bot.setWebhook('https://ps5-alert-bot.herokuapp.com/' + '1418644151')

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
