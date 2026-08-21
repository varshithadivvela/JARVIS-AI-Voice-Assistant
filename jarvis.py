import os
import numpy as np
import sounddevice as sd
import soundfile as sf
import librosa
from sklearn.preprocessing import StandardScaler
import random
import warnings
import pyttsx3
import speech_recognition as sr
import pyaudio
import datetime
import time
import webbrowser
import pyautogui
import sys
import json
import psutil
import cv2
import speedtest
import requests
from requests import get
from bs4 import BeautifulSoup
import winsound
from playsound import playsound
import threading
from time import sleep
import pywhatkit
import pyjokes
import streamlit as st
import re
from concurrent.futures import ThreadPoolExecutor
import asyncio
from groq import Groq

# Configure Streamlit page
st.set_page_config(
    page_title="Jarvis AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Groq client
client = Groq(api_key="your_actual_groq_api_key")

# Authentication sentences
AUTHENTICATION_SENTENCES = [
    "The quick brown fox jumps over the lazy dog",
    "Artificial intelligence is changing the way we interact with technology",
    "Secure access should never be compromised by weak authentication",
    "Voice recognition systems are reliable when trained correctly",
    "Technology should adapt to humans, not the other way around"
]

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'is_authenticated' not in st.session_state:
    st.session_state.is_authenticated = False
if 'is_listening' not in st.session_state:
    st.session_state.is_listening = False
if 'processing_task' not in st.session_state:
    st.session_state.processing_task = None
if 'assistant_active' not in st.session_state:
    st.session_state.assistant_active = False
if 'voice_profiles' not in st.session_state:
    st.session_state.voice_profiles = {}
if 'show_registration' not in st.session_state:
    st.session_state.show_registration = False
if 'registration_name' not in st.session_state:
    st.session_state.registration_name = ""
if 'current_sentence' not in st.session_state:
    st.session_state.current_sentence = ""
if 'auth_feedback' not in st.session_state:
    st.session_state.auth_feedback = {"status": None, "message": ""}
if 'just_registered' not in st.session_state:
    st.session_state.just_registered = False
if 'clap_detected' not in st.session_state:
    st.session_state.clap_detected = False

# Personal contacts (would normally be stored securely)
person1_name= "9xxxxxxxxxxx"
person2_name= "9xxxxxxxxxxx"
group_name= "group_chat_id"

class VoiceAuthenticator:
    def __init__(self, registered_voices_folder=r"C:\Users\harshi\OneDrive\Documents\Jarvis\voice"):
        self.registered_voices_folder = registered_voices_folder
        self.sample_rate = 16000
        self.duration = 5
        self.base_threshold = 0.55  # Reduced threshold for better recognition
        self.scaler = StandardScaler()
        
        os.makedirs(self.registered_voices_folder, exist_ok=True)
        self.load_voice_profiles()
        self.prepare_scaler()

    def prepare_scaler(self):
        """Prepare scaler with all available features"""
        if st.session_state.voice_profiles:
            all_features = list(st.session_state.voice_profiles.values())
            self.scaler.fit(all_features)

    def extract_features(self, audio, sr):
        """More robust feature extraction"""
        audio = librosa.util.normalize(audio)
        mfccs = librosa.feature.mfcc(
            y=audio, 
            sr=sr, 
            n_mfcc=13,
            n_fft=2048,
            hop_length=512
        )
        return np.mean(mfccs.T, axis=0)

    def load_voice_profiles(self):
        """Load existing voice samples from folder"""
        for file in os.listdir(self.registered_voices_folder):
            if file.endswith((".wav", ".mp3")):
                try:
                    name = os.path.splitext(file)[0]
                    audio, sr = librosa.load(
                        os.path.join(self.registered_voices_folder, file),
                        sr=self.sample_rate
                    )
                    features = self.extract_features(audio, sr)
                    st.session_state.voice_profiles[name] = features
                except Exception as e:
                    st.error(f"Error processing {file}: {e}")

    def compare_voice(self, input_features):
        """More accurate voice comparison"""
        input_features = self.scaler.transform([input_features])[0]
        results = {}
        
        for name, stored_features in st.session_state.voice_profiles.items():
            stored_features = self.scaler.transform([stored_features])[0]
            similarity = np.dot(input_features, stored_features) / (
                np.linalg.norm(input_features) * np.linalg.norm(stored_features))
            normalized_score = (similarity + 1) / 2
            results[name] = normalized_score
        
        return results

    def record_voice(self):
        """Record voice sample with volume normalization"""
        try:
            st.info(f"Please say: \"{st.session_state.current_sentence}\"")
            recording = sd.rec(
                int(self.duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=1,
                dtype='float32'
            )
            sd.wait()
            
            temp_path = os.path.join(self.registered_voices_folder, "temp_recording.wav")
            sf.write(temp_path, recording, self.sample_rate)
            
            audio, sr = librosa.load(temp_path, sr=self.sample_rate)
            if librosa.get_duration(y=audio, sr=sr) < 1.0:
                st.warning("Recording too short, please try again")
                os.remove(temp_path)
                return None
                
            return temp_path
        except Exception as e:
            st.error(f"Recording error: {e}")
            return None

    def register_voice(self, name):
        """Registration with better guidance"""
        st.info(f"Registering voice for: {name}")
        st.session_state.current_sentence = random.choice(AUTHENTICATION_SENTENCES)
        sample_path = self.record_voice()
        
        if sample_path is None:
            return False
            
        try:
            audio, sr = librosa.load(sample_path, sr=self.sample_rate)
            features = self.extract_features(audio, sr)
            new_path = os.path.join(self.registered_voices_folder, f"{name}.wav")
            os.rename(sample_path, new_path)
            
            st.session_state.voice_profiles[name] = features
            self.prepare_scaler()
            st.session_state.auth_feedback = {
                "status": "success",
                "message": "Voice registered successfully! Now please authenticate."
            }
            st.session_state.just_registered = True
            return True
        except Exception as e:
            st.error(f"Registration failed: {e}")
            if os.path.exists(sample_path):
                os.remove(sample_path)
            st.session_state.auth_feedback = {
                "status": "error",
                "message": f"Registration failed: {str(e)}"
            }
            return False

    def authenticate_voice(self):
        """Voice authentication for Jarvis access"""
        if not st.session_state.voice_profiles:
            st.session_state.auth_feedback = {
                "status": "error",
                "message": "No voices registered yet! Please register first."
            }
            st.session_state.show_registration = True
            return False
            
        st.session_state.current_sentence = random.choice(AUTHENTICATION_SENTENCES)
        sample_path = self.record_voice()
        
        if sample_path is None:
            st.session_state.auth_feedback = {
                "status": "error",
                "message": "Failed to record voice sample. Please try again."
            }
            return False
            
        try:
            audio, sr = librosa.load(sample_path, sr=self.sample_rate)
            input_features = self.extract_features(audio, sr)
            results = self.compare_voice(input_features)
            
            best_match, best_score = max(results.items(), key=lambda x: x[1])
            effective_threshold = min(self.base_threshold + 0.01*len(st.session_state.voice_profiles), 0.65)  # Adjusted threshold
            
            if len(results) > 1:
                score_diff = sorted(results.values(), reverse=True)[0] - sorted(results.values(), reverse=True)[1]
            else:
                score_diff = 0.5  # Lowered difference requirement
                
            if best_score > effective_threshold and score_diff > 0.05:  # More lenient difference
                st.session_state.auth_feedback = {
                    "status": "success",
                    "message": f"Authentication successful! Welcome back, {best_match}."
                }
                return True
            else:
                st.session_state.auth_feedback = {
                    "status": "error",
                    "message": f"Authentication failed. Voice not recognized (score: {best_score:.2f}, threshold: {effective_threshold:.2f}). Please try again."
                }
                st.session_state.show_registration = True
                return False
        
        except Exception as e:
            st.session_state.auth_feedback = {
                "status": "error",
                "message": f"Authentication error: {str(e)}"
            }
            return False
        finally:
            if os.path.exists(sample_path):
                os.remove(sample_path)

# Initialize voice authenticator
voice_auth = VoiceAuthenticator()

def initialize_engine():
    """Initialize the text-to-speech engine"""
    try:
        engine = pyttsx3.init("sapi5")
        voices = engine.getProperty('voices')
        if len(voices) > 1:
            engine.setProperty('voice', voices[1].id)
        rate = engine.getProperty('rate')
        engine.setProperty('rate', rate-50)
        volume = engine.getProperty('volume')
        engine.setProperty('volume', volume+0.25)
        return engine
    except Exception as e:
        st.error(f"Failed to initialize speech engine: {e}")
        return None

def speak(text, show_message=True):
    """Convert text to speech and optionally display in Streamlit"""
    try:
        engine = initialize_engine()
        if engine:
            engine.say(text)
            engine.runAndWait()
       
        if show_message:
            st.session_state.messages.append({"role": "assistant", "content": text})
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(text)
        return True
    except Exception as e:
        st.error(f"Speech synthesis error: {str(e)}")
        return False

def listen_for_command():
    """Listen for voice commands"""
    r = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration=0.5)
            st.info("🎤 Listening...")
            audio = r.listen(source, timeout=5)
       
        st.info("🔍 Recognizing...")
        query = r.recognize_google(audio, language='en-in')
       
        st.session_state.messages.append({"role": "user", "content": query})
        with st.chat_message("user", avatar="👤"):
            st.markdown(query)
       
        return query
    except sr.UnknownValueError:
        st.warning("Could not understand audio. Please try again.")
        return "None"
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return "None"

def cal_day():
    """Calculate current day of the week"""
    day = datetime.datetime.today().weekday() + 1
    day_dict = {
        1: "Monday", 2: "Tuesday", 3: "Wednesday", 4: "Thursday",
        5: "Friday", 6: "Saturday", 7: "Sunday"
    }
    return day_dict.get(day, "Unknown")

def wishMe():
    """Greet the user based on time of day"""
    hour = int(datetime.datetime.now().hour)
    t = time.strftime("%I:%M %p")
    day = cal_day()
    today_date = datetime.datetime.now().strftime("%B %d, %Y")

    if hour >= 0 and hour < 12:
        greeting = f"Good morning! It's {day}, {today_date} and the time is {t}"
    elif hour >= 12 and hour < 16:
        greeting = f"Good afternoon! It's {day}, {today_date} and the time is {t}"
    else:
        greeting = f"Good evening! It's {day}, {today_date} and the time is {t}"
   
    return greeting

def get_current_time():
    """Get current time in 12-hour format with AM/PM"""
    current_time = datetime.datetime.now().strftime("%I:%M %p")
    return f"The current time is {current_time}"

def extract_time(raw_text):
    """Extract time from text input"""
    raw_text = raw_text.lower().replace(".", "").replace("p m", "pm").replace("a m", "am")

    # Case 1: Match "7:35 pm" or "07:35pm"
    match = re.search(r'(\d{1,2}):?(\d{2})\s?(am|pm)', raw_text)
    if match:
        hour, minute, period = match.groups()
        formatted = f"{int(hour)}:{minute} {period.upper()}"
        return formatted
   
    return None

def measure_ambient_noise(seconds=2):
    """Measure ambient noise level"""
    st.info("Measuring ambient noise... Please stay silent.")
    recording = sd.rec(int(seconds * 44100), samplerate=44100, channels=1, dtype='float32')
    sd.wait()
    peak = np.max(np.abs(recording))
    st.info(f"Ambient peak volume: {peak:.6f}")
    return peak

def detect_clap():
    """Improved clap detection function"""
    st.info("Preparing to detect clap...")
    
    # Measure ambient noise first
    ambient_peak = measure_ambient_noise()
    threshold = ambient_peak * 3  # Clap should be significantly louder than ambient
    
    st.info(f"Clap detection threshold set to: {threshold:.6f}")
    st.info("Listening for clap... (clap your hands now)")
    
    try:
        # Record for 3 seconds
        recording = sd.rec(int(3 * 44100), samplerate=44100, channels=1, dtype='float32')
        sd.wait()
        
        # Find the maximum amplitude in the recording
        max_amplitude = np.max(np.abs(recording))
        st.info(f"Detected peak amplitude: {max_amplitude:.6f}")
        
        if max_amplitude > threshold:
            st.session_state.clap_detected = True
            st.success("Clap detected!")
            return True
        else:
            st.session_state.clap_detected = False
            st.warning("No clap detected.")
            return False
            
    except Exception as e:
        st.error(f"Error detecting clap: {e}")
        return False

def Get_Mob_or_GID(Person):
    """Get mobile number or group ID from contacts"""
    country_code = "+91"
    Mob_or_GID = ""
    Person = str(Person).lower()
    if "person1_name" in Person:
        Mob_or_GID = country_code + person1_name
    elif "person2_name" in Person:
        Mob_or_GID = country_code + person2_name
    elif "group_name" in Person:
        Mob_or_GID = group_name
    else:
        Mob_or_GID = "Person or Group not found in the contact. Please add it."

    return Mob_or_GID

def IsGroup(Person):
    """Check if contact is a group"""
    M_or_ID = str(Get_Mob_or_GID(Person))
    if M_or_ID.isdigit():
        return False
    else:
        return True

def IsinContact(Person):
    """Check if person is in contacts"""
    if Get_Mob_or_GID(Person).startswith("Person"):
        return False
    else:
        return True
   
def Send_msg_whatsapp_Grp(ID, Msg):
    """Send WhatsApp message to group"""
    pywhatkit.sendwhatmsg_to_group_instantly(ID, Msg, wait_time=10)
    time.sleep(8)
    pyautogui.click(2792, 1623)#your laptop screen configurations

def Send_msg_whatsapp_indivisual(Mob, Msg):
    """Send WhatsApp message to individual"""
    pywhatkit.sendwhatmsg_instantly(Mob, Msg, wait_time=10)
    time.sleep(8)
    pyautogui.click(2792, 1623)#your laptop screen configurations

def temperature(loc):
    """Get current temperature for location"""
    try:
        city = loc
        response = requests.get(f"https://wttr.in/{city}?format=3")
        result = f"Current weather: {response.text}"
        speak(result)
        return result
    except Exception as e:
        error = f"Error: {e}"
        speak(error)
        return error

def play_music(command):
    """Play music from local directory"""
    try:
        music_dir = 'C:\\Users\\........'  # Change to your music directory
        songs = os.listdir(music_dir)
       
        song_name = command.replace('play', '').strip().lower()
       
        matching_songs = [song for song in songs if song_name in song.lower() and song.endswith('.mp3')]

        if matching_songs:
            os.startfile(os.path.join(music_dir, matching_songs[0]))
            result = f"Playing {matching_songs[0]}"
            speak(result)
            return result
        else:
            result = f"Sorry, I couldn't find the song '{song_name}' in your music directory."
            speak(result)
            return result
    except Exception as e:
        result = "An unexpected error occurred."
        speak(result)
        return f"{result}\nError: {e}"

def alarm(Timing):
    """Threaded alarm function"""
    def run_alarm():
        try:
            alarm_time = datetime.datetime.strptime(Timing, "%I:%M %p").time()
            speak(f"Alarm has been set for {Timing}")
            while True:
                now = datetime.datetime.now().time()
                if now.hour == alarm_time.hour and now.minute == alarm_time.minute:
                    for _ in range(5):
                        winsound.Beep(1000, 1000)  # Beep 5 times
                    break
                time.sleep(10)  # Check every 10 seconds
        except Exception as e:
            speak(f"Alarm error: {e}")
    threading.Thread(target=run_alarm).start()
    return "Alarm scheduled successfully."

def Reminder(Timing, text):
    """Threaded reminder function"""
    def run_reminder():
        try:
            reminder_time = datetime.datetime.strptime(Timing, "%I:%M %p").time()
            speak(f"Reminder has been set for {Timing}")
            while True:
                now = datetime.datetime.now().time()
                if now.hour == reminder_time.hour and now.minute == reminder_time.minute:
                    for _ in range(3):
                        speak(text)
                        time.sleep(1)
                    break
                time.sleep(10)  # Check every 10 seconds
        except Exception as e:
            speak(f"Reminder error: {e}")
    threading.Thread(target=run_reminder).start()
    return "Reminder scheduled successfully."

def social_media(user_command):
    """Open social media platforms"""
    if 'facebook' in user_command:
        speak("Opening Facebook")
        webbrowser.open("https://www.facebook.com/")
    elif 'whatsapp' in user_command:
        speak("Opening WhatsApp")
        webbrowser.open("https://web.whatsapp.com/")
    elif 'discord' in user_command:
        speak("Opening Discord")
        webbrowser.open("https://discord.com/")
    elif 'instagram' in user_command:
        speak("Opening Instagram")
        webbrowser.open("https://www.instagram.com/")
    return True

def schedule():
    """Get today's schedule"""
    day = cal_day().lower()
    speak("Checking today's schedule")
    week = {
        "monday": "From 9:00 to 9:50 you have Algorithms class, from 10:00 to 11:50 you have System Design class, from 12:00 to 2:00 you have a break, and today you have Programming Lab from 2:00 onwards.",
        "tuesday": "From 9:00 to 9:50 you have Web Development class, from 10:00 to 10:50 you have a break, from 11:00 to 12:50 you have Database Systems class, from 1:00 to 2:00 you have a break, and today you have Open Source Projects lab from 2:00 onwards.",
        "wednesday": "Today you have a full day of classes. From 9:00 to 10:50 you have Machine Learning class, from 11:00 to 11:50 you have Operating Systems class, from 12:00 to 12:50 you have Ethics in Technology class, from 1:00 to 2:00 you have a break, and today you have Software Engineering workshop from 2:00 onwards.",
        "thursday": "Today you have a full day of classes. From 9:00 to 10:50 you have Computer Networks class, from 11:00 to 12:50 you have Cloud Computing class, from 1:00 to 2:00 you have a break, and today you have Cybersecurity lab from 2:00 onwards.",
        "friday": "Today you have a full day of classes. From 9:00 to 9:50 you have Artificial Intelligence class, from 10:00 to 10:50 you have Advanced Programming class, from 11:00 to 12:50 you have UI/UX Design class, from 1:00 to 2:00 you have a break, and today you have Capstone Project work from 2:00 onwards.",
        "saturday": "Today you have a more relaxed day. From 9:00 to 11:50 you have team meetings for your Capstone Project, from 12:00 to 12:50 you have Innovation and Entrepreneurship class, from 1:00 to 2:00 you have a break, and today you have extra time to work on personal development and coding practice from 2:00 onwards.",
        "sunday": "Today is a holiday, but keep an eye on upcoming deadlines and use this time to catch up on any reading or project work."
    }
   
    schedule_text = week.get(day, "No schedule found for today.")
    speak(schedule_text)
    return True

def openApp(user_command):
    """Open system applications"""
    if "calculator" in user_command:
        speak("Opening calculator")
        os.startfile('C:\\Windows\\System32\\calc.exe')
    elif "notepad" in user_command:
        speak("Opening notepad")
        os.startfile('C:\\Windows\\System32\\notepad.exe')
    elif "paint" in user_command:
        speak("Opening paint")
        os.startfile('C:\\Windows\\System32\\mspaint.exe')
    return True

def closeApp(user_command):
    """Close system applications"""
    if "calculator" in user_command:
        speak("Closing calculator")
        os.system('taskkill /f /im calc.exe')
    elif "notepad" in user_command:
        speak("Closing notepad")
        os.system('taskkill /f /im notepad.exe')
    elif "paint" in user_command:
        speak("Closing paint")
        os.system('taskkill /f /im mspaint.exe')
    return True

def condition():
    """Check system condition"""
    try:
        usage = str(psutil.cpu_percent())
        speak(f"CPU is at {usage} percentage")
       
        battery = psutil.sensors_battery()
        if battery:
            percentage = battery.percent
            speak(f"Our system has {percentage} percentage battery")
           
            if percentage >= 80:
                speak("We have enough charging to continue our work")
            elif percentage >= 40 and percentage <= 75:
                speak("We should connect our system to charging point to charge our battery")
            else:
                speak("We have very low power, please connect to charging otherwise the system may shut down")
        else:
            speak("Battery information not available on this system")
    except Exception as e:
        speak("Unable to get system condition")
    return True

def webCam():    
    speak('Opening camera')
    try:
        cap = cv2.VideoCapture(0)
        while True:
            ret, img = cap.read()
            cv2.imshow('web camera',img)
            k = cv2.waitKey(50)
            if k == 27:
                break
        cap.release()
        cv2.destroyAllWindows()
    except Exception as e:
        speak("Unable to open camera")
    return True

def InternetSpeed():
    try:
        speak("Wait a few seconds, checking your internet speed")
        st.info("Testing internet speed...")
        s_t = speedtest.Speedtest()
        dl = s_t.download()
        dl = dl/(1000000) #converting bytes to megabytes
        up = s_t.upload()
        up = up/(1000000)
        print(dl,up)
        speak(f"We have {dl:.2f} megabytes per second downloading speed and {up:.2f} megabytes per second uploading speed")
    except Exception as e:
        speak("Unable to test internet speed")
    return True

def scshot():
    """Take a screenshot"""
    try:
        speak("Please tell me the name for this screenshot file")
        name = listen_for_command()
        if name == "None":
            name = "screenshot"
           
        speak("Please hold the screen for few seconds, I am taking screenshot")
        time.sleep(3)
        img = pyautogui.screenshot()
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{timestamp}.png"
        img.save(filename)
        speak(f"Screenshot saved as {filename}")
    except Exception as e:
        speak("Unable to take screenshot")
    return True

def location():
    """Get current location"""
    try:
        speak("Wait, let me check")
        IP_Address = get('https://api.ipify.org').text
        url = 'https://get.geojs.io/v1/ip/geo/' + IP_Address + '.json'
        geo_request = get(url)
        geo_data = geo_request.json()
        city = geo_data['city']
        state = geo_data['region']
        country = geo_data['country']
        tZ = geo_data['timezone']
        longitude = geo_data['longitude']
        latidute = geo_data['latitude']
        org = geo_data['organization_name']
        result = f"I think we are in {city} city of {state} state of {country} country"
        speak(result)
        speak(f"We are in {tZ} timezone, the latitude is {latidute}, and the longitude is {longitude}, using {org}'s network")
    except Exception as e:
        speak("Sorry, due to network issue I am not able to find our location.")
    return True

def Tell_Joke():
    """Tell a random joke"""
    try:
        c = ['neutral', 'chuck', 'all']
        category = random.choice(c)
        return pyjokes.get_joke(category=category)
    except:
        return "Why don't scientists trust atoms? Because they make up everything!"

def news():
    """Fetch and read latest news"""
    try:
        YOUR_NEWS_API_KEY = "your_newsapi_key"
        MAIN_URL = f"https://newsapi.org/v2/top-headlines?sources=techcrunch&apiKey={YOUR_NEWS_API_KEY}"
        MAIN_PAGE = get(MAIN_URL).json()
        articles = MAIN_PAGE['articles']
        headings = []
        seq = ['first', 'second', 'third', 'fourth', 'fifth']
       
        for ar in articles:
            headings.append(ar['title'])
       
        for i in range(min(len(seq), len(headings))):
            news_text = f"Today's {seq[i]} news is: {headings[i]}"
            speak(news_text)
       
        speak("I have read the latest news")
    except Exception as e:
        speak("Unable to fetch news at the moment")
    return True

def handle_general_queries(query):
    """Handle general conversational queries"""
    query_lower = query.lower()
   
    if "today's date" in query_lower or "what's the date" in query_lower:
        today_date = datetime.datetime.now().strftime("%B %d, %Y")
        response = f"Today's date is {today_date}"
        speak(response)
    elif "hi" in query_lower or "hello" in query_lower:
        responses = ["Hello!", "Hi there!", "Greetings!"]
        response = random.choice(responses)
        speak(response)
    elif "how are you" in query_lower:
        responses = ["I'm doing well, thank you!", "I'm great, how about you?", "All systems functioning normally!"]
        response = random.choice(responses)
        speak(response)
    elif "thank you" in query_lower or "thanks" in query_lower:
        responses = ["You're welcome!", "Happy to help!", "My pleasure!"]
        response = random.choice(responses)
        speak(response)
    elif "what can you do" in query_lower:
        response = "I can help with scheduling, playing music, setting alarms, sending messages, checking weather, and much more!"
        speak(response)
    elif "who are you" in query_lower:
        response = "I'm Jarvis, your personal AI assistant."
        speak(response)
    elif "time" in query_lower or "current time" in query_lower:
        response = get_current_time()
        speak(response)
    else:
        try:
            response = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{"role": "user", "content": query}]
            ).choices[0].message.content
            speak(response)
        except Exception as e:
            speak("I'm sorry, I didn't understand that. Could you please rephrase?")
    return True

def process_command(query):
    """Process a single command and return the result"""
    query_lower = query.lower()
   
    try:
        if any(x in query_lower for x in ['facebook', 'discord', 'whatsapp', 'instagram']):
            return social_media(query_lower)
        elif any(x in query_lower for x in ["university time table", "schedule"]):
            return schedule()
        elif any(x in query_lower for x in ["volume up", "increase volume"]):
            pyautogui.press("volumeup")
            return speak("Volume increased")
        elif any(x in query_lower for x in ["volume down", "decrease volume"]):
            pyautogui.press("volumedown")
            return speak("Volume decreased")
        elif any(x in query_lower for x in ["volume mute", "mute sound"]):
            pyautogui.press("volumemute")
            return speak("Volume muted")
        elif any(x in query_lower for x in ["open calculator", "open notepad", "open paint"]):
            return openApp(query_lower)
        elif any(x in query_lower for x in ["close calculator", "close notepad", "close paint"]):
            return closeApp(query_lower)
        elif any(x in query_lower for x in ["system condition", "condition of the system"]):
            speak("Checking the system condition")
            return condition()
        elif 'webcam' in query_lower:
            return webCam()
        elif "internet speed" in query_lower:
            return InternetSpeed()
        elif any(x in query_lower for x in ['take screenshot', 'take the screenshot', "take a screenshot"]):
            return scshot()
        elif any(x in query_lower for x in ['tell me news', "the news", "today's news"]):
            speak("Please wait, fetching the latest news")
            return news()
        elif 'ip address' in query_lower:
            ip = get('https://api.ipify.org').text
            return speak(f"Your IP address is {ip}")
        elif 'location' in query_lower:
            return location()
        elif 'weather' in query_lower:
            speak("Tell me the city name")
            city = listen_for_command().lower()
            return temperature(city)
        elif 'play music' in query_lower:
            speak("Which song do you want to play?")
            name = listen_for_command().lower()
            return play_music(name)
        elif "alarm" in query_lower:
            speak("Alright! Set it for when?")
            Timing = listen_for_command().lower()
            Timing = extract_time(Timing)
            return alarm(Timing)
        elif any(x in query_lower for x in ["reminder", "set reminder"]):
            speak("What is your reminder?")
            reminder = listen_for_command().lower()
            speak("When you want to set the reminder?")
            Timming = listen_for_command().lower()
            Timming = extract_time(Timming)
            return Reminder(Timming, reminder)
        elif "send message" in query_lower:
            speak("To whom you want to send message?")
            Person = listen_for_command().lower()
            if IsinContact(Person):
                contactInfo = Get_Mob_or_GID(Person)
                speak("What message you want to send?")
                Msg = listen_for_command().lower()
                if IsGroup(Person):
                    result = Send_msg_whatsapp_Grp(contactInfo, Msg)
                else:
                    result = Send_msg_whatsapp_indivisual(contactInfo, Msg)
                return speak(result)
            else:
                return speak(Get_Mob_or_GID(Person))
        elif any(x in query_lower for x in ['joke', "make me laugh", "make me smile", "make me happy"]):
            speak("Sure, here is a joke")
            joke = Tell_Joke()
            return speak(joke)
        elif any(x in query_lower for x in ["detect clap", "detect", "clap"]):
            if detect_clap():
                return speak("Clap detected!")
            else:
                return speak("Clap not detected")
        elif 'youtube' in query_lower:
            speak("what do you want to watch")
            song = listen_for_command().lower()
            if "play" in song:
                song = song.replace("play", "")
            speak(f'Playing {song} on YouTube')
            pywhatkit.playonyt(song)
            return True
        elif 'spotify' in query_lower:
            speak("OK! what do you want to listen to?")
            music = listen_for_command().lower()
            music = music.replace("play", "")
            webbrowser.open(f'https://open.spotify.com/search/{music}')
            sleep(19)
            pyautogui.click(1574, 890)
            return True
        elif any(x in query_lower for x in ["exit", "goodbye", "quit"]):
            speak("Goodbye! Have a great day!")
            st.session_state.assistant_active = False
            return "exit"
        else:
            return handle_general_queries(query)
    except Exception as e:
        error_msg = f"Error processing command: {str(e)}"
        st.error(error_msg)
        speak("Sorry, I encountered an error processing that command.")
        return False

def registration_form():
    """Display the voice registration form"""
    with st.form("voice_registration"):
        st.subheader("🔒 Voice Registration")
        name = st.text_input("Enter your name", value=st.session_state.registration_name)
        submitted = st.form_submit_button("Register Voice")
        
        if submitted and name:
            if voice_auth.register_voice(name):
                st.session_state.show_registration = False
                st.rerun()
            else:
                st.error("Registration failed. Please try again.")


def main():
    """Main Streamlit application"""
    st.title("🤖 Jarvis AI Assistant")
    st.markdown("Your personal AI assistant powered by voice recognition and advanced AI")
    
    # Show authentication feedback if available
    if st.session_state.auth_feedback["status"]:
        if st.session_state.auth_feedback["status"] == "success":
            st.success(st.session_state.auth_feedback["message"])
            speak(st.session_state.auth_feedback["message"], show_message=False)
            
            # After successful authentication, greet the user
            if not st.session_state.just_registered:
                greeting = wishMe()
                speak(greeting)
            else:
                st.session_state.just_registered = False
        else:
            st.error(st.session_state.auth_feedback["message"])
            speak(st.session_state.auth_feedback["message"], show_message=False)
        st.session_state.auth_feedback = {"status": None, "message": ""}
    
    # Show registration form if needed
    if st.session_state.show_registration:
        registration_form()
        return
    
    # Sidebar for controls and settings
    with st.sidebar:
        st.header("🎛️ Controls")
        
        # Authentication section
        if not st.session_state.is_authenticated:
            st.subheader("🔒 Authentication")
            if st.button("🎤 Voice Authentication", use_container_width=True):
                speak("Please read the sentence on screen for authentication", show_message=False)
                if voice_auth.authenticate_voice():
                    st.session_state.is_authenticated = True
                    st.rerun()
                else:
                    st.rerun()
        
        else:
            st.success("✅ Authenticated")
            
            # Voice management section
            st.subheader("🗣️ Voice Management")
            if st.button("Register New Voice", use_container_width=True):
                st.session_state.show_registration = True
                st.session_state.registration_name = ""
                st.rerun()
            
            # Assistant controls
            st.subheader("🎮 Assistant Controls")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🎤 Listen", use_container_width=True):
                    if not st.session_state.is_listening:
                        st.session_state.is_listening = True
                        query = listen_for_command()
                        if query != "None":
                            result = process_command(query)
                            if result == "exit":
                                st.session_state.is_authenticated = False
                                st.session_state.assistant_active = False
                        st.session_state.is_listening = False
                        st.rerun()
            
            with col2:
                if st.button("🔄 Reset", use_container_width=True):
                    st.session_state.messages = []
                    st.session_state.is_authenticated = False
                    st.session_state.is_listening = False
                    st.rerun()
        
        # Quick commands
        if st.session_state.is_authenticated:
            st.subheader("⚡ Quick Commands")
            
            quick_commands = [
                ("📅 Schedule", "schedule"),
                ("🌐 Social Media", "open facebook"),
                ("📰 News", "tell me news"),
                ("🎵 YouTube", "play music on youtube"),
                ("🌦️ Weather", "what's the weather"),
                ("⏰ Set Alarm", "set alarm"),
                ("🔔 Set Reminder", "set reminder"),
                ("💬 Send Message", "send message"),
                ("💻 System Status", "system condition"),
                ("📍 Location", "location"),
                ("🌐 Internet Speed", "internet speed"),
                ("📸 Screenshot", "take screenshot"),
                ("😂 Tell Joke", "tell me a joke"),
                ("👏 Detect Clap", "detect clap"),
                ("🕒 Current Time", "what time is it"),
            ]
            
            for label, command_text in quick_commands:
                if st.button(label, use_container_width=True):
                    result = process_command(command_text)
                    st.rerun()
        
        # Settings
        st.subheader("⚙️ Settings")
        
        # Voice settings
        speech_rate = st.slider("🗣️ Speech Rate", 150, 300, 200)
        speech_volume = st.slider("🔊 Speech Volume", 0.0, 1.0, 0.8)
        
        # System info
        st.subheader("📊 System Info")
        try:
            cpu_usage = psutil.cpu_percent()
            memory_usage = psutil.virtual_memory().percent
            
            st.metric("CPU Usage", f"{cpu_usage}%")
            st.metric("Memory Usage", f"{memory_usage}%")
            
            battery = psutil.sensors_battery()
            if battery:
                st.metric("Battery", f"{battery.percent}%")
        except:
            st.info("System info unavailable")
    
    # Main chat interface
    st.subheader("💬 Chat Interface")
    
    # Display chat messages
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"], avatar="🤖" if message["role"] == "assistant" else "👤"):
                st.markdown(message["content"])
    
    # Text input as alternative to voice
    if st.session_state.is_authenticated:
        if prompt := st.chat_input("Type your command here (or use voice button in sidebar)"):
            # Add user message to chat
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user", avatar="👤"):
                st.markdown(prompt)
            
            # Process the command
            result = process_command(prompt)
            if result == "exit":
                st.session_state.is_authenticated = False
                st.session_state.assistant_active = False
            
            st.rerun()
    
    # Status indicator
    status_container = st.container()
    with status_container:
        if st.session_state.is_listening:
            st.info("🎤 Listening for your command...")
        elif not st.session_state.is_authenticated:
            st.warning("🔒 Please authenticate to use Jarvis")
        else:
            st.success("✅ Jarvis is ready! Use voice button or type your command")


if __name__ == "__main__":
    main()
