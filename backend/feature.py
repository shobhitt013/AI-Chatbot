import os
import struct
import subprocess
import time
import webbrowser
import sqlite3
import pyautogui
import pyaudio
import pvporcupine
import eel
import pywhatkit as kit
import pygame
from shlex import quote
from hugchat import hugchat
from backend.command import speak
from backend.config import ASSISTANT_NAME
from backend.helper import extract_yt_term, remove_words

# Initialize database connection
conn = sqlite3.connect("jarvis.db")
cursor = conn.cursor()

# Initialize pygame mixer
pygame.mixer.init()

# Play assistant start sound
@eel.expose
def play_assistant_sound():
    sound_file = r"F:\Jarvis-2025-master\Jarvis-2025-master\frontend\assets\audio\start_sound.mp3"  # Use raw string for file path
    pygame.mixer.music.load(sound_file)
    pygame.mixer.music.play()

# Open an application or website based on the user command
def openCommand(query):
    query = query.replace(ASSISTANT_NAME, "").replace("open", "").strip()
    query = query.lower()

    app_name = query

    if app_name != "":
        try:
            cursor.execute('SELECT path FROM sys_command WHERE name IN (?)', (app_name,))
            results = cursor.fetchall()

            if results:
                speak(f"Opening {query}")
                os.startfile(results[0][0])

            else:
                cursor.execute('SELECT url FROM web_command WHERE name IN (?)', (app_name,))
                results = cursor.fetchall()

                if results:
                    speak(f"Opening {query}")
                    webbrowser.open(results[0][0])

                else:
                    speak(f"Opening {query}")
                    try:
                        os.system(f'start {query}')
                    except Exception as e:
                        print(f"Error opening app: {e}")
                        speak("Application not found")
        except Exception as e:
            print(f"Database query error: {e}")
            speak("Something went wrong while processing your request")

# Play YouTube video based on query
def PlayYoutube(query):
    search_term = extract_yt_term(query)
    speak(f"Playing {search_term} on YouTube")
    kit.playonyt(search_term)

# Hotword detection (wake word like "jarvis" or "alexa")
def hotword():
    porcupine = None
    paud = None
    audio_stream = None
    try:
        porcupine = pvporcupine.create(keywords=["jarvis", "alexa"])
        paud = pyaudio.PyAudio()
        audio_stream = paud.open(
            rate=porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=porcupine.frame_length
        )

        while True:
            keyword = audio_stream.read(porcupine.frame_length)
            keyword = struct.unpack_from("h" * porcupine.frame_length, keyword)
            keyword_index = porcupine.process(keyword)

            if keyword_index >= 0:
                print("Hotword detected")
                pyautogui.keyDown("win")
                pyautogui.press("j")
                time.sleep(2)
                pyautogui.keyUp("win")

    except Exception as e:
        print(f"Hotword detection error: {e}")
    finally:
        if porcupine is not None:
            porcupine.delete()
        if audio_stream is not None:
            audio_stream.close()
        if paud is not None:
            paud.terminate()

# Find contact from database for WhatsApp or call
def findContact(query):
    words_to_remove = [ASSISTANT_NAME, 'make', 'a', 'to', 'phone', 'call', 'send', 'message', 'whatsapp', 'video']
    query = remove_words(query, words_to_remove).strip().lower()

    try:
        cursor.execute(
            "SELECT Phone FROM contacts WHERE LOWER(name) LIKE ? OR LOWER(name) LIKE ?",
            ('%' + query + '%', query + '%')
        )
        results = cursor.fetchall()

        if results:
            mobile_number_str = str(results[0][0])

            if not mobile_number_str.startswith('+91'):
                mobile_number_str = '+91' + mobile_number_str

            print(f"Found contact: {mobile_number_str}")
            return mobile_number_str, query
        else:
            speak("Contact not found")
            return 0, 0
    except Exception as e:
        print(f"Contact lookup error: {e}")
        speak("Error finding contact")
        return 0, 0

# Send WhatsApp message, make call or video call
def whatsApp(Phone, message, flag, name):
    if flag == 'message':
        target_tab = 12
        jarvis_message = f"Message sent successfully to {name}"
    elif flag == 'call':
        target_tab = 7
        message = ''
        jarvis_message = f"Calling {name}"
    else:
        target_tab = 6
        message = ''
        jarvis_message = f"Starting video call with {name}"

    # Encode the message for the URL
    encoded_message = quote(message)
    whatsapp_url = f"whatsapp://send?phone={Phone}&text={encoded_message}"
    full_command = f'start "" "{whatsapp_url}"'

    try:
        subprocess.run(full_command, shell=True)
        time.sleep(5)
        subprocess.run(full_command, shell=True)

        pyautogui.hotkey('ctrl', 'f')
        for _ in range(1, target_tab):
            pyautogui.hotkey('tab')
        pyautogui.hotkey('enter')

        speak(jarvis_message)
    except Exception as e:
        print(f"WhatsApp interaction error: {e}")
        speak("Failed to interact with WhatsApp")

# Chatbot interaction using HugChat
def chatBot(query):
    user_input = query.lower()
    try:
        chatbot = hugchat.ChatBot(cookie_path=r"backend\cookie.json")
        id = chatbot.new_conversation()
        chatbot.change_conversation(id)
        response = chatbot.chat(user_input)
        print(response)
        speak(response)
        return response
    except Exception as e:
        print(f"Chatbot error: {e}")
        speak("Chatbot is currently unavailable")
        return "I'm sorry, I couldn't process your request."

