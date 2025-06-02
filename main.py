import os
import eel
from backend.auth.recoganize import AuthenticateFace  # Assuming your file is actually 'recoganize.py'
from backend.feature import *
from backend.command import *

def start():
    # Initialize eel with frontend directory
    eel.init("frontend")

    @eel.expose
    def init():
        eel.hideLoader()
        speak("Welcome to Jarvis")
        speak("Ready for Face Authentication")
        
        flag = AuthenticateFace()

        if flag == 1:
            speak("Face recognized successfully")
            eel.hideFaceAuth()
            eel.hideFaceAuthSuccess()
            speak("Welcome to Your Assistant")
            eel.hideStart()
            play_assistant_sound()  # Play startup sound after success
        else:
            speak("Face not recognized. Please try again")

    # Start the eel server
    eel.start("index.html", mode='chrome', host="localhost", block=True)
