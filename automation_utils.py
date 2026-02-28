import os
import subprocess
from fpdf import FPDF
import smtplib
from email.message import EmailMessage
from config import USER_EMAIL, USER_PHONE, BASE_DIR
import json
import requests
from googlesearch import search

import pyperclip
import pywhatkit as kit
import webbrowser

def open_application(app_name):
    """
    Opens common applications. Add more as needed.
    """
    apps = {
        "code": "code",
        "vscode": "code",
        "browser": "start chrome",
        "chrome": "start chrome",
        "edge": "start msedge",
        "notepad": "notepad",
        "calculator": "calc",
        "explorer": "explorer"
    }
    
    app_command = apps.get(app_name.lower())
    if app_command:
        try:
            subprocess.Popen(app_command, shell=True)
            return True
        except Exception as e:
            print(f"Error opening {app_name}: {e}")
            return False
    return False

def open_folder(folder_name):
    """
    Opens common system folders.
    """
    folders = {
        "documents": os.path.expanduser("~/Documents"),
        "downloads": os.path.expanduser("~/Downloads"),
        "desktop": os.path.expanduser("~/Desktop"),
        "music": os.path.expanduser("~/Music"),
        "pictures": os.path.expanduser("~/Pictures"),
        "videos": os.path.expanduser("~/Videos")
    }
    
    folder_path = folders.get(folder_name.lower())
    if folder_path and os.path.exists(folder_path):
        try:
            os.startfile(folder_path)
            return True
        except Exception as e:
            print(f"Error opening folder {folder_name}: {e}")
            return False
    return False

def read_text():
    """
    Reads text from the clipboard.
    """
    try:
        text = pyperclip.paste()
        if text:
            return text
        return "Your clipboard is empty."
    except Exception as e:
        print(f"Error reading clipboard: {e}")
        return "I couldn't read your clipboard."

def send_whatsapp(number, message):
    """
    Sends a WhatsApp message using pywhatkit. 
    Note: Requires WhatsApp Web login in the default browser.
    """
    try:
        # This will open the browser and send the message instantly
        kit.sendwhatmsg_instantly(f"+91{number}", message, wait_time=15, tab_close=True)
        return True
    except Exception as e:
        print(f"Error sending WhatsApp: {e}")
        return False

MEMORY_FILE = os.path.join(BASE_DIR, "memory.json")

def remember_info(key, value):
    """
    Saves information to a persistent JSON memory file.
    """
    memory = {}
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'r') as f:
            try:
                memory = json.load(f)
            except json.JSONDecodeError:
                memory = {}
    
    memory[key.lower()] = value
    with open(MEMORY_FILE, 'w') as f:
        json.dump(memory, f, indent=4)
    return True

def get_remembered_info(key):
    """
    Retrieves information from the memory file.
    """
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'r') as f:
            try:
                memory = json.load(f)
                return memory.get(key.lower(), "I don't remember anything about that.")
            except:
                return "My memory is a bit fuzzy right now."
    return "I don't have any memory yet."

def search_web(query):
    """
    Searches the web and returns top results.
    """
    try:
        results = []
        # Limiting to top 3 for brevity in voice
        for j in search(query, num=3, stop=3, pause=2):
            results.append(j)
        return results
    except Exception as e:
        print(f"Error searching web: {e}")
        return []

def create_pdf(text, filename="output.pdf"):
# ... (rest of the file remains same)
    """
    Creates a simple PDF document with the given text.
    """
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, txt=text)
        pdf.output(filename)
        return True
    except Exception as e:
        print(f"Error creating PDF: {e}")
        return False

def send_email(to_email, subject, body):
    """
    Sends an email using SMTP. 
    Note: Requires a valid app password for Gmail or other providers.
    """
    # This is a placeholder as it requires real credentials
    # For a real implementation, you'd pull these from environment variables or a secure store
    FROM_EMAIL = USER_EMAIL
    PASSWORD = "your_app_password" # PLACEHOLDER
    
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = FROM_EMAIL
    msg['To'] = to_email

    try:
        # Example for Gmail:
        # with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        #     smtp.login(FROM_EMAIL, PASSWORD)
        #     smtp.send_message(msg)
        print(f"SIMULATION: Sending email to {to_email} with subject '{subject}'")
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
