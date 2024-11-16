import os
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackContext, filters

TOKEN = '7889993616:AAG0n0O6OT6OChFHQkAnkn7lBbbvhGYnYV4'
async def start(update: Update, context: CallbackContext):
    await context.bot.send_message(chat_id=update.effective_chat.id, text='Send me a link to download the video or photo!')

async def handle_message(update: Update, context: CallbackContext):
    url = update.message.text
    if not is_valid_url(url):
        return  # Do not send any response if the message is not a valid link
    await download_video(url, update.effective_chat.id, context)
   

def is_valid_url(url):
    # Basic URL validation (you can improve this)
    return url.startswith('http://') or url.startswith('https://')

async def download_video(url, chat_id, context):
    file_name = None
    try:
        # Set up yt-dlp options for video
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',  # Download best video and audio
            'outtmpl': 'downloads/%(title)s.%(ext)s',  # Save to downloads folder
            'noplaylist': True,  # Download only single video
        }

        # Create downloads directory if it doesn't exist
        if not os.path.exists('downloads'):
            os.makedirs('downloads')

        # Download the media
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_name = ydl.prepare_filename(info)

        # Check if the URL contains "reel"
        if "reel" in url.lower():
            # If the URL contains "reel", treat it as a video
            with open(file_name, 'rb') as video_file:
                await context.bot.send_video(chat_id=chat_id, video=video_file)
        else:
            # Determine the file extension
            file_extension = os.path.splitext(file_name)[1].lower()

            # Check the file extension to determine if it's an image
            if file_extension in ['.jpg', '.jpeg', '.png', '.gif']:  # Add more image formats as needed
                with open(file_name, 'rb') as photo_file:
                    await context.bot.send_photo(chat_id=chat_id, photo=photo_file)
            else:
                # Handle other media types or unknown types
                await context.bot.send_message(chat_id=chat_id, text='The downloaded media is neither a video nor an image.')

    except Exception as e:
        print(f"An error occurred while downloading media: {e}")
        await context.bot.send_message(chat_id=chat_id, text='An error occurred while downloading the media.')
    finally:
        # Clean up the file after sending or if an error occurred
        if file_name and os.path.exists(file_name):
            os.remove(file_name)

def main():
    application = ApplicationBuilder().token(TOKEN).build()
    start_handler = CommandHandler('start', start)
    message_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    
    application.add_handler(start_handler)
    application.add_handler(message_handler)
    
    application.run_polling()

if __name__ == '__main__':
    main()
