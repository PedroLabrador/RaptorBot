import os
import logging
import lyricsgenius
from dotenv import load_dotenv
from telegram import MessageEntity
from telegram.ext import Filters
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from igramscraper.instagram import Instagram
from igramscraper.exception import InstagramException
from emojis import TREX_EMOJI


load_dotenv()
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

updater = Updater(token=os.getenv("RAPTOR_TELEGRAM_API_KEY"), use_context=True)
genius  = lyricsgenius.Genius(os.getenv("GENIUS_ACCESS_KEY"), verbose=True)
ig      = Instagram(sleep_between_requests=0)
cwd     = os.getcwd() + os.path.sep + 'ig_sessions' + os.path.sep
ig.with_credentials(os.getenv('IG_RAPTOR_USERNAME'), os.getenv('IG_RAPTOR_PASSWORD'), session_folder=cwd, use_old_sessions=True)


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Rawr")


def help_command(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Marico el que lo lea")


def lyrics(update, context):
    genius.excluded_terms = ["(Remix)", "(Live)"]
    genius.remove_section_headers = True
    text_search = " ".join(context.args)
    song = genius.search_song(text_search)

    try:
        lyrics = f"{song.artist} - {song.title}\n\n{song.lyrics}"
        context.bot.send_message(chat_id=update.effective_chat.id, text=lyrics)
    except AttributeError:
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"Not found {TREX_EMOJI}")


def url(update, context):
    message = update.message.text
    if 'instagram' in message:
        url = message.split("?", 1)[0]
        try:
            media = ig.get_media_by_url(url)
        except InstagramException:
            logging.info("Cookies expired, logging in..")
            ig.login()
            media = ig.get_media_by_url(url)
        context.bot.send_video(chat_id=update.effective_chat.id, video=media.video_standard_resolution_url)


def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"{TREX_EMOJI} ???")


updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('help', help_command))
updater.dispatcher.add_handler(CommandHandler('lyrics', lyrics))
updater.dispatcher.add_handler(MessageHandler(Filters.text & (Filters.entity(MessageEntity.URL) | Filters.entity(MessageEntity.TEXT_LINK)), url))
updater.dispatcher.add_handler(MessageHandler(Filters.command, unknown))

updater.start_polling()
updater.idle()
