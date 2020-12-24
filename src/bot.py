# built-in modules
import os
import json
from pathlib import Path
from datetime import datetime

# local
from helpers import timestamp_now
from datautils import get_paper, TelegramUser, create_new_user_db, add_paper_to_user
from constants import project_root

# external modules
import telegram
from telegram import MessageEntity
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    Filters,
)
from markkk.logger import logger


logs_path: Path = project_root / "logs"

if not logs_path.is_dir():
    os.mkdir(str(logs_path))

##############################################
# user log function

def user_log(update, ts: str = None, remarks: str = ""):
    if not ts:
        ts: str = timestamp_now()
    first_name: str = update.message.chat.first_name
    last_name: str = update.message.chat.last_name
    username: str = update.message.chat.username
    chat_id: str = update.message.chat.id
    name: str = f"{first_name} {last_name}"
    record: str = (
        f"{ts} - chat_id({chat_id}) - username({username}) - name({name}) - visited({remarks})\n"
    )
    user_log_fp: Path = logs_path / "user_visit_history.txt"
    with user_log_fp.open(mode="a") as f:
        f.write(record)

def get_current_telegram_user(update) -> TelegramUser:
    first_name: str = update.message.chat.first_name
    last_name: str = update.message.chat.last_name
    username: str = update.message.chat.username
    return TelegramUser(username, first_name, last_name)


##############################################
# Error Handlers
def error(update, context):
    """
    Error Handler: Log Errors caused by Updates.
    """
    logger.error(f'Update "{update}" \ncaused following error: \n"{context.error}"')

##############################################
# Command Handlers

def start(update, context):
    """
    Command Handler: /start 
    """
    user = get_current_telegram_user(update)
    msg = f"Hi {user.first_name}, this is paper bot"
    update.message.reply_text(msg, parse_mode=telegram.ParseMode.MARKDOWN)
    create_new_user_db(user)
    user_log(update, remarks="/start")


def help(update, context):
    """
    Command Handler: /help 
    """
    msg = "Currently I can only accpet arxiv.org url"
    update.message.reply_text(msg, parse_mode=telegram.ParseMode.MARKDOWN)
    user_log(update, remarks="/help")


def source(update, context):
    """
    Command Handler: /source
    """
    msg = "View source / contribute / report issue on [GitHub](https://github.com/MarkHershey/paperbot)"
    update.message.reply_text(msg, parse_mode=telegram.ParseMode.MARKDOWN)
    user_log(update, remarks="/source")

############################################################################################
# MessageHandlers 

def url_MsgHandler(update, context):
    # context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)
    try:
        url_received = update.message.text

        if "arxiv" in url_received:
            logger.debug("URL identified: arXiv")

            paper = get_paper(url_received)
            msg = "*Paper*: {}\n\n*Author*: {}\n\n*PDF*: {}".format(
                paper.title, paper.first_author, paper.pdf_url
            )

            user = get_current_telegram_user(update)
            add_paper_to_user(paper, user)

        elif "openaccess.thecvf.com" in url_received:
            logger.debug("URL identified: CVPR Open Access")
            msg = "CVPR Open Access (in development)"

        else:
            msg = "Currently only arxiv paper url is supported."

    except Exception as err:
        logger.error(err)
        msg = "Internal Server Error"
        # msg = telegram.utils.helpers.escape_markdown(msg)
    
    # respond to user
    update.message.reply_text(msg, parse_mode=telegram.ParseMode.MARKDOWN)
    user_log(update, remarks="respond_paper_info_from_url")


############################################################################################

def main():
    """
    Bot start up process
    """
    config_fp = project_root / "src/config.conf"
    if not config_fp.is_file():
        logger.error("No Config File is Found.")
        return

    try:
        with config_fp.open() as f:
            config = json.load(f)
        bot_token: str = config["bot_token"]
        if bot_token == "REPLACE_ME":
            raise Exception()
    except Exception as e:
        logger.error("Failed getting bot token from 'config.conf'")
        return

    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(bot_token, use_context=True)
    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Command Handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help))
    dispatcher.add_handler(CommandHandler("source", source))

    # Message Handlers
    url_filter = Filters.text & (
        Filters.entity(MessageEntity.URL) | Filters.entity(MessageEntity.TEXT_LINK)
    )
    dispatcher.add_handler(MessageHandler(url_filter, url_MsgHandler))

    # log all errors
    dispatcher.add_error_handler(error)

    # Start the Bot
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
