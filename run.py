import multiprocessing
from main import start
from backend.feature import hotword

def startJarvis():
    print("Process 1: Starting JARVIS System...")
    try:
        start()
    except Exception as e:
        print(f"Error in startJarvis: {e}")

def listenHotword():
    print("Process 2: Starting Hotword Detection...")
    try:
        hotword()
    except Exception as e:
        print(f"Error in listenHotword: {e}")

if __name__ == "__main__":
    # Create processes
    process1 = multiprocessing.Process(target=startJarvis)
    process2 = multiprocessing.Process(target=listenHotword)

    # Start processes
    process1.start()
    process2.start()

    # Join process1 (main system)
    
    process1.join()

    # If hotword detection is still running after GUI closes, terminate it
    if process2.is_alive():
        process2.terminate()
        print("Process 2 (Hotword Detection) terminated.")
        process2.join()

    print("System is fully terminated.")
