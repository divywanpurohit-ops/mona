import speech_recognition as sr
import pyttsx3
import os
import datetime
import tempfile
import automation_utils
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
import threading
from config import ASSISTANT_NAME, WAKE_WORD, STOP_WORD, INTERACTIONS_LOG, USER_NAME, TELEGRAM_TOKEN, AUTHORIZED_USER_ID

# Initialize Text-to-Speech engine
engine = pyttsx3.init()
voices = engine.getProperty('voices')
# Setting to Microsoft Hazel (Female, UK) - often sounds 'sweeter'
if len(voices) > 1:
    engine.setProperty('voice', voices[1].id) 
else:
    engine.setProperty('voice', voices[0].id)

engine.setProperty('rate', 145) # Slower rate for a more gentle tone

def speak(text):
    print(f"{ASSISTANT_NAME}: {text}")
    engine.say(text)
    engine.runAndWait()
    log_interaction(f"Assistant: {text}")

import sounddevice as sd
import numpy as np
import wave
import tempfile

def listen(duration=5):
    """
    Records audio using sounddevice and converts it to text using SpeechRecognition.
    If audio devices are not available, falls back to manual text input.
    """
    try:
        fs = 44100  # Sample rate
        print("Listening (Voice)...")
        
        # Record audio
        recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
        sd.wait()  # Wait until recording is finished
        
        # Save recording to a temporary wav file
        temp_dir = tempfile.gettempdir()
        temp_wav = os.path.join(temp_dir, "mona_temp_audio.wav")
        
        with wave.open(temp_wav, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2) # 16-bit
            wf.setframerate(fs)
            wf.writeframes(recording.tobytes())

        # Recognize using SpeechRecognition
        r = sr.Recognizer()
        with sr.AudioFile(temp_wav) as source:
            audio = r.record(source)
        
        print("Recognizing...")
        query = r.recognize_google(audio, language='en-in')
        print(f"User said: {query}\n")
        log_interaction(f"User: {query}")
        return query.lower()
    except Exception as e:
        print(f"Voice detection unavailable or failed: {e}")
        print("Falling back to text input.")
        user_input = input("You (Type command): ")
        log_interaction(f"User (Text): {user_input}")
        return user_input.lower()

def log_interaction(text):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(INTERACTIONS_LOG, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {text}\n")

def process_command(query):
    if "open" in query:
        app_name = query.replace("open", "").strip()
        
        # Check if it's a folder
        folders = ["documents", "downloads", "desktop", "music", "pictures", "videos"]
        if app_name in folders:
            if automation_utils.open_folder(app_name):
                speak(f"Opening your {app_name} folder.")
            else:
                speak(f"I couldn't find the {app_name} folder.")
        # Otherwise try to open as an application
        elif automation_utils.open_application(app_name):
            speak(f"Opening {app_name}")
        else:
            speak(f"I'm sorry, I don't know how to open {app_name}")

    elif "whatsapp" in query or "message" in query:
        speak("Whom should I message? Please tell me the phone number without country code.")
        number = listen()
        speak("What is the message?")
        msg = listen()
        if number != "None" and msg != "None":
            speak("Sending message. Please make sure WhatsApp Web is logged in.")
            automation_utils.send_whatsapp(number, msg)
        else:
            speak("I couldn't get the number or message.")

    elif "read" in query or "clipboard" in query:
        text = automation_utils.read_text()
        speak("Sure, reading from your clipboard.")
        speak(text)

    elif "remember" in query or "yaad" in query:
        speak("What should I remember?")
        info = listen()
        if info != "None":
            speak(f"Sure, I will remember that: {info}")
            automation_utils.remember_info("last_note", info)
        else:
            speak("I didn't catch that.")

    elif "what do you remember" in query or "yaad hai" in query:
        info = automation_utils.get_remembered_info("last_note")
        speak(f"Last you told me: {info}")

    elif "search" in query or "events" in query or "news" in query:
        speak("What should I search for?")
        search_query = listen()
        if search_query != "None":
            speak(f"Searching for {search_query}...")
            results = automation_utils.search_web(search_query)
            if results:
                speak("I found some results. I'm opening the first one for you.")
                import webbrowser
                webbrowser.open(results[0])
            else:
                speak("I couldn't find anything recent on that.")
        else:
            speak("I didn't get the search query.")

    elif "pdf" in query or "create a pdf" in query:
        speak("What text should I include in the PDF?")
        content = listen()
        if content != "None":
            filename = f"doc_{datetime.datetime.now().strftime('%Y%H%M%S')}.pdf"
            if automation_utils.create_pdf(content, filename):
                speak(f"PDF created successfully as {filename}")
            else:
                speak("Failed to create PDF.")
        else:
            speak("I didn't catch that. PDF creation cancelled.")

    elif "email" in query or "send email" in query:
        speak("Who is the recipient?")
        # For simulation, we'll just ask for the name/email
        recipient = listen()
        speak("What is the subject?")
        subject = listen()
        speak("What is the message?")
        message = listen()
        
        if recipient != "None" and subject != "None" and message != "None":
            if automation_utils.send_email(recipient, subject, message):
                speak(f"Email sent to {recipient}")
            else:
                speak("Failed to send email.")
        else:
            speak("Email details incomplete. Cancelled.")

    elif "next page" in query:
        speak("Moving to the next page.")
        # This can be expanded based on what 'page' means (e.g. key press)
        import pyautogui
        pyautogui.press('pgdn')

    elif STOP_WORD in query:
        speak("Stopping, sir. Goodbye!")
        return False

    elif query == "none":
        pass
    
    else:
        speak("I'm not sure how to help with that yet, but I'm learning.")
    
    return True

async def handle_telegram_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    user_id = update.message.from_user.id
    
    if AUTHORIZED_USER_ID and user_id != AUTHORIZED_USER_ID:
        await update.message.reply_text("Unauthorized access.")
        return

    log_interaction(f"Telegram Text ({user_id}): {user_text}")
    print(f"Telegram Command: {user_text}")
    process_command(user_text.lower())
    await update.message.reply_text(f"Action triggered on laptop: {user_text}")

async def handle_telegram_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if AUTHORIZED_USER_ID and user_id != AUTHORIZED_USER_ID:
        await update.message.reply_text("Unauthorized access.")
        return

    voice = update.message.voice
    file = await context.bot.get_file(voice.file_id)
    
    # Download the voice file
    temp_dir = tempfile.gettempdir()
    ogg_path = os.path.join(temp_dir, f"voice_{user_id}.ogg")
    wav_path = os.path.join(temp_dir, f"voice_{user_id}.wav")
    await file.download_to_drive(ogg_path)

    try:
        # Convert OGG to WAV using pydub
        from pydub import AudioSegment
        audio = AudioSegment.from_ogg(ogg_path)
        audio.export(wav_path, format="wav")

        # Recognize using SpeechRecognition
        r = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            audio_data = r.record(source)
        
        query = r.recognize_google(audio_data, language='en-in').lower()
        log_interaction(f"Telegram Voice ({user_id}): {query}")
        print(f"Telegram Voice Command: {query}")
        
        process_command(query)
        await update.message.reply_text(f"Voice action triggered: {query}")
    except Exception as e:
        print(f"Error processing Telegram voice: {e}")
        await update.message.reply_text("I couldn't understand that voice message.")
    finally:
        if os.path.exists(ogg_path): os.remove(ogg_path)
        if os.path.exists(wav_path): os.remove(wav_path)

def run_telegram_bot():
    if TELEGRAM_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
        print("Telegram Token not set. Phone integration disabled.")
        return

    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    # Handlers for both text and voice
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_telegram_message))
    application.add_handler(MessageHandler(filters.VOICE, handle_telegram_voice))
    
    print("Telegram Bot is running (Text & Voice supported)...")
    application.run_polling()

def main():
    # Start Telegram Bot in a separate thread
    threading.Thread(target=run_telegram_bot, daemon=True).start()
    
    speak(f"Hello {USER_NAME}, I am {ASSISTANT_NAME}. How can I help you today?")
    
    while True:
        query = listen()
        
        if WAKE_WORD in query:
            speak("Yes sir, Okay boss. What can I do for you?")
            
            while True:
                command = listen()
                if command == "None":
                    continue
                
                if STOP_WORD in command:
                    speak("Stopping. I will wait for you to call my name again.")
                    break
                
                if not process_command(command):
                    return # Exit the whole app if needed, or just break
        
        elif STOP_WORD in query:
            speak("Exiting program.")
            break

if __name__ == "__main__":
    main()
