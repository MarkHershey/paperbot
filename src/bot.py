# built-in modules
import os
import json
from pathlib import Path
from datetime import datetime

# local
from data.datautils import get_paper

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

project_root: Path = Path(__file__).resolve().parent.parent
logs_path: Path = project_root / "logs"

if not logs_path.is_dir():
    os.mkdir(str(logs_path))

##############################################
# helper functions

def timestamp_now() -> str:
    """ return a timestamp in string: YYYYMMDDHHMMSS"""
    now: str = str(datetime.now())
    ts: str = ""
    for i in now[:-7]:
        if i in (" ", "-", ":"):
            pass
        else:
            ts += i
    return ts


def user_log(update, ts: str = None, remarks: str = ""):
    if not ts:
        ts: str = timestamp_now()
    first_name: str = update.message.chat.first_name
    last_name: str = update.message.chat.last_name
    username: str = update.message.chat.username
    id: str = update.message.chat.id
    name: str = f"{first_name} {last_name}"
    record: str = (
        f"{ts} - id({id}) - username({username}) - name({name}) - visited({remarks})\n"
    )
    user_log_fp: Path = logs_path / "user_visit_history.txt"
    with user_log_fp.open(mode="a") as f:
        f.write(record)

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
    msg = "Hi {}, this is paper bot".format(update.message.chat.first_name)
    update.message.reply_text(msg, parse_mode=telegram.ParseMode.MARKDOWN)
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

def respond_paper_info_from_url(update, context):
    # context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)
    try:
        message_received = update.message.text
        if "arxiv" in message_received:
            paper = get_paper(message_received)
            msg = "*Paper*: {}\n\n*Author*: {}\n\n*PDF*: {}".format(
                paper.title, paper.first_author, paper.pdf_url
            )
            print(msg)
        else:
            msg = "Currently only arxiv paper url is supported."
    except Exception as err:
        logger.error(err)
        msg = "Internal Server Error"
    update.message.reply_text(msg, parse_mode=telegram.ParseMode.MARKDOWN)
    user_log(update, remarks="respond_paper_info_from_url")

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
        elif "openaccess.thecvf.com" in url_received:
            logger.debug("URL identified: CVPR Open Access")
            msg = "CVPR Open Access (in development)"
        else:
            msg = "Currently only arxiv paper url is supported."
    except Exception as err:
        logger.error(err)
        msg = "Internal Server Error"
    
    # respond to user
    # msg = telegram.utils.helpers.escape_markdown(msg)
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
