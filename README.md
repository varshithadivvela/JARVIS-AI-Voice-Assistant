# JARVIS-AI-Voice-Assistant
A Python-based AI voice assistant with voice authentication, speech recognition, automation, and conversational AI.

🤖 J.A.R.V.I.S – AI Voice Assistant

An AI-powered voice assistant built with Python and Streamlit that combines speech recognition, natural language processing, computer vision, generative AI, automation, translation, and system utilities into a single intelligent assistant.

J.A.R.V.I.S. can authenticate users through voice, respond to natural-language queries, detect a clap to activate the assistant, provide contextual responses using LLaMA 3 through the Groq API, translate text, send WhatsApp messages, play YouTube content, provide news updates, schedule reminders, capture screenshots, and perform basic system diagnostics.

---

🚀 Features

🎙️ Voice Interaction

- Speech-to-text using SpeechRecognition
- Text-to-speech using pyttsx3
- Natural-language voice commands
- Context-aware responses

🔐 Voice Authentication

- Voice-based user authentication
- MFCC-based voice feature extraction
- Authentication before accessing assistant functionality

👏 Clap Detection

- Detects a clap sound through the microphone
- Can be used as an activation mechanism for the assistant

🧠 Generative AI

- AI-powered conversational responses
- Uses LLaMA 3 through the Groq API
- Handles general questions and contextual conversations

🌐 Translation

- Automatic translation of responses
- Supports multiple languages using Deep Translator

📱 WhatsApp Automation

- Send WhatsApp messages using voice commands
- Uses PyWhatKit for WhatsApp automation

▶️ YouTube Integration

- Search and play YouTube videos
- Voice-controlled YouTube playback

📰 News Updates

- Retrieves news using a news API
- Provides current news information to the user

⏰ Reminders & Alarms

- Schedule reminders
- Set alarms using voice commands

📸 Screenshot Capture

- Capture screenshots through voice commands

🖥️ System Diagnostics

- Performs basic system-related checks
- Provides information about system status

🖥️ Streamlit Interface

- Interactive web-based interface
- Displays assistant responses and application status
- Provides a simple interface for interacting with J.A.R.V.I.S.

---

🧠 Project Architecture

                         ┌───────────────────┐
                         │      User         │
                         └─────────┬─────────┘
                                   │
                         Voice / Text Input
                                   │
                                   ▼
                         ┌───────────────────┐
                         │    Streamlit UI   │
                         └─────────┬─────────┘
                                   │
                                   ▼
                         ┌───────────────────┐
                         │ Speech Recognition│
                         └─────────┬─────────┘
                                   │
                                   ▼
                         ┌───────────────────┐
                         │ Command Processing│
                         └─────────┬─────────┘
                                   │
                  ┌────────────────┼────────────────┐
                  │                │                │
                  ▼                ▼                ▼
             Generative AI    Automation       Utilities
                  │                │                │
                  ▼                ▼                ▼
              LLaMA 3          WhatsApp       Reminders
              Groq API         YouTube         News
                               Translation     Screenshots
                               etc.
                  │
                  ▼
                         ┌───────────────────┐
                         │   Assistant Reply  │
                         └─────────┬─────────┘
                                   │
                         ┌─────────┴─────────┐
                         ▼                   ▼
                  Text Response        Voice Response
                                      (pyttsx3)

---

🛠️ Technologies Used

Technology| Purpose
Python| Core programming language
Streamlit| User interface
SpeechRecognition| Speech-to-text
pyttsx3| Text-to-speech
OpenCV| Computer vision and audio-related processing
PyWhatKit| WhatsApp and YouTube automation
Deep Translator| Language translation
Groq API| Generative AI responses
LLaMA 3| Large language model
News API| News retrieval
NumPy| Numerical and signal processing operations
MFCC| Voice authentication features

---

🔐 Voice Authentication

J.A.R.V.I.S. includes a voice authentication mechanism based on Mel-Frequency Cepstral Coefficients (MFCC).

The authentication pipeline can be represented as:

Voice Input
     ↓
Audio Capture
     ↓
MFCC Feature Extraction
     ↓
Voice Feature Comparison
     ↓
Authentication
     ↓
Access to Assistant

This adds an additional layer of personalization and security to the assistant.

«Note: This is an educational voice-authentication implementation and should not be considered a production-grade biometric security system.»

---

👏 Clap Detection

The project includes clap detection as an alternative activation mechanism.

Microphone Input
       ↓
Audio Signal
       ↓
Signal Processing
       ↓
Clap Detection
       ↓
Activate J.A.R.V.I.S.

This allows the assistant to respond to a predefined audio trigger.

---

🤖 Generative AI with LLaMA 3

J.A.R.V.I.S. integrates a large language model through the Groq API.

The LLM component is responsible for generating natural-language responses to user queries.

User Query
    ↓
Command Processor
    ↓
Groq API
    ↓
LLaMA 3
    ↓
Generated Response
    ↓
J.A.R.V.I.S.

The API key is loaded through an environment variable rather than being stored directly in the source code.

---

🌍 Multilingual Translation

The assistant can translate generated responses into a selected language using Deep Translator.

Example workflow:

User Query
     ↓
AI Response
     ↓
Translation
     ↓
Selected Language
     ↓
Text / Voice Output

---

📱 WhatsApp Automation

J.A.R.V.I.S. can automate WhatsApp messaging through voice commands.

Example workflow:

Voice Command
     ↓
Identify Recipient
     ↓
Generate Message
     ↓
PyWhatKit
     ↓
WhatsApp

The feature requires WhatsApp Web and an appropriate browser environment.

---

▶️ YouTube Integration

Users can interact with YouTube using voice commands.

Examples include:

"Play [song/video] on YouTube"

J.A.R.V.I.S. processes the command and uses PyWhatKit to open/play the requested content.

---

📰 News Updates

The assistant can retrieve news information through a news API and present relevant updates to the user.

User:
"Tell me today's news"

       ↓

J.A.R.V.I.S.
       ↓
News API
       ↓
News Results
       ↓
Voice / Text Response

---

⏰ Reminders and Alarms

The assistant supports scheduling reminders and alarms through voice commands.

Example:

"Set an alarm for 7 AM"

The assistant processes the command and schedules the requested action.

---

📸 Screenshot Capture

J.A.R.V.I.S. can capture screenshots when requested through a supported command.

Example:

"Take a screenshot"

The application captures the current screen and saves the image locally.

---

🖥️ Streamlit Interface

The project uses Streamlit to provide an interactive interface.

The interface can display:

- Assistant status
- User commands
- AI responses
- Translation output
- Application controls
- Voice interaction status

---

📂 Project Structure

jarvis-ai-voice-assistant/
│
├── jarvis.py
├── README.md
├── requirements.txt
├── .gitignore
│
└── assets/
    └── screenshots/

If additional files are required by your implementation, they can be added to the repository while keeping API keys and generated files excluded.

---

⚙️ Installation

1. Clone the Repository

git clone https://github.com/YOUR-USERNAME/jarvis-ai-voice-assistant.git
cd jarvis-ai-voice-assistant

2. Create a Virtual Environment

python -m venv venv

Activate it on Windows:

venv\Scripts\activate

On macOS/Linux:

source venv/bin/activate

3. Install Dependencies

pip install -r requirements.txt

---

🔑 API Configuration

J.A.R.V.I.S. uses external APIs for some functionality.

Create a ".env" file in the project directory:

GROQ_API_KEY=your_groq_api_key
NEWS_API_KEY=your_news_api_key

Then load the variables in Python using "python-dotenv".

⚠️ Security

Never upload your ".env" file or API keys to GitHub.

Do not write:

GROQ_API_KEY = "actual-secret-key"

Instead use environment variables.

---

▶️ Running the Application

After installing the dependencies and configuring the required API keys:

streamlit run jarvis.py

The Streamlit application will start locally and provide a browser-based interface.

---

🎤 Example Commands

J.A.R.V.I.S. can respond to commands such as:

"Who are you?"

"Play a song on YouTube"

"Send a WhatsApp message"

"Translate this into Telugu"

"Tell me the latest news"

"Set an alarm"

"Take a screenshot"

"Check my system"

The exact commands supported depend on the implementation in "jarvis.py".

---

🔄 Overall Workflow

Start J.A.R.V.I.S.
        ↓
Voice Authentication
        ↓
Activation / Clap Detection
        ↓
Capture User Command
        ↓
Speech-to-Text
        ↓
Command Classification
        ↓
┌─────────────────────────────────┐
│                                 │
▼                                 ▼
AI Query                     Specific Action
│                                 │
▼                                 ▼
LLaMA 3                      YouTube / WhatsApp
Groq API                     News / Translation
│                            Reminder / Screenshot
└──────────────┬──────────────────┘
               ↓
         Generate Response
               ↓
       Text-to-Speech Output
               ↓
             User

---

🎯 Key Learning Outcomes

This project provided practical experience with:

- Python application development
- Speech recognition
- Text-to-speech systems
- Natural Language Processing
- Generative AI
- Large Language Models
- API integration
- Voice authentication
- MFCC feature extraction
- Audio signal processing
- Computer vision
- Web automation
- Translation APIs
- Streamlit application development
- Event-driven automation
- Environment variable management

---

🔮 Future Improvements

Possible improvements include:

- Add wake-word detection
- Improve voice authentication accuracy
- Add a conversation history system
- Add long-term memory
- Add Retrieval-Augmented Generation (RAG)
- Add local LLM support
- Improve intent classification
- Add more computer-control capabilities
- Add weather integration
- Add calendar integration
- Add email automation
- Add a more advanced Streamlit UI
- Add authentication and user profiles
- Add logging and error monitoring
- Deploy the application as a web service

---

⚠️ Limitations

- Some features require an active internet connection.
- External APIs may have usage limits.
- WhatsApp automation depends on WhatsApp Web and browser behavior.
- Voice recognition can be affected by background noise.
- Voice authentication is intended for educational purposes.
- Some operating-system features may behave differently across Windows, Linux, and macOS.
- API-dependent functionality requires valid API credentials.

---

👩‍💻 Author

NagaVenkataLakshmi HamsaVarshitha Divvela

B.Tech – Computer Science & Engineering (AI & ML)

RVR & JC College of Engineering

2025 Graduate

---

⭐ Project

If you find this project interesting, consider giving the repository a ⭐ on GitHub.

---

📌 Disclaimer

J.A.R.V.I.S. is an educational AI assistant project created to demonstrate the integration of artificial intelligence, natural language processing, speech technologies, computer vision, APIs, and automation.

The project is not affiliated with or endorsed by Marvel, Iron Man, or any related intellectual property.
