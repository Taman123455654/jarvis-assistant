import speech_recognition as sr
import pyttsx3
import requests
import json
import re
import os
import subprocess
import webbrowser
import getpass

# Configuration
API_KEY = "your_real_openrouter_api_key_here"
API_URL = "https://openrouter.ai/api/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://your-site-or-project.com",
    "X-Title": "Jarvis Assistant"
}

# Initialize TTS engine
engine = pyttsx3.init()
engine.setProperty("rate", 180)

recognizer = sr.Recognizer()
microphone = sr.Microphone()

# Speak function
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Listen function
def listen():
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        print("🎤 Listening...")
        try:
            audio = recognizer.listen(source, timeout=5)
            print("🔍 Recognizing...")
            return recognizer.recognize_google(audio)
        except (sr.UnknownValueError, sr.WaitTimeoutError):
            return None

# Clean response
def clean_response(text):
    return re.sub(r'\s{2,}', ' ', re.sub(r'\\n|\n|\r|[*_#>\[\]{}|]', ' ', text)).strip()

# Chat with OpenRouter/DeepSeek
def chat_with_deepseek(prompt):
    try:
        data = {
            "model": "deepseek/deepseek-chat",
            "messages": [
                {"role": "system", "content": "You are Jarvis, a helpful AI assistant."},
                {"role": "user", "content": prompt}
            ]
        }
        response = requests.post(API_URL, headers=HEADERS, data=json.dumps(data))
        if response.ok:
            result = response.json()
            return clean_response(result["choices"][0]["message"]["content"])
        else:
            print("❌ API Error:", response.status_code, response.text)
            return "Sorry, there was a problem reaching the AI."
    except Exception as e:
        print("❌ Exception:", str(e))
        return "Sorry, an error occurred while connecting to the AI."

# Control functions
def shutdown():
    speak("Shutting down the system.")
    os.system("shutdown /s /t 1")

def open_chrome():
    speak("Opening Chrome.")
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    if os.path.exists(chrome_path):
        subprocess.Popen([chrome_path])
    else:
        speak("Chrome is not installed at the default location.")

def search_google(query):
    speak(f"Searching Google for {query}")
    webbrowser.open(f"https://www.google.com/search?q={query}")

def open_folder(folder_name):
    username = getpass.getuser()
    folder_path = os.path.join("C:\\Users", username, folder_name)
    if os.path.exists(folder_path):
        speak(f"Opening folder {folder_name}")
        os.startfile(folder_path)
    else:
        speak("Sorry, I can't find that folder.")

# Main loop
if __name__ == "__main__":
    speak("Hello, I am Jarvis. Say 'Jarvis' to activate me.")
    while True:
        print("🕒 Waiting for wake word 'Jarvis'...")
        wake_input = listen()
        if wake_input and "jarvis" in wake_input.lower():
            speak("Yes? What would you like me to do?")
            command = listen()

            if command:
                command_lower = command.lower()

                if any(word in command_lower for word in ["exit", "quit", "stop", "bye"]):
                    speak("Goodbye! Have a great day.")
                    break
                elif "shutdown" in command_lower:
                    shutdown()
                    break
                elif "open chrome" in command_lower:
                    open_chrome()
                elif "search for" in command_lower or "google" in command_lower:
                    search_query = command_lower.replace("search for", "").replace("google", "").strip()
                    if search_query:
                        search_google(search_query)
                    else:
                        speak("What should I search for?")
                elif "open folder" in command_lower:
                    folder = command_lower.replace("open folder", "").strip()
                    open_folder(folder)
                else:
                    response = chat_with_deepseek(command)
                    speak(response)
            else:
                speak("Sorry, I didn't catch that.")


