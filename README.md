AI Adaptive Tutor — Personalized Learning System
This project is an AI-powered adaptive tutor designed to help users learn any topic through a fully personalized and dynamic learning experience.

Demo video:
https://youtu.be/f9RnM4ek-I8

Overview
Users can ask questions on any subject, and the system generates a structured learning path adapted to their level.
The AI continuously adjusts the content based on user performance, ensuring an efficient and personalized learning experience.
To reinforce understanding, the system provides targeted exercises and feedback, helping users progress step by step without getting stuck.

Key Features
- Multi-agent architecture for specialized reasoning and task handling
- Adaptive learning loop based on user performance and mistakes
- Persistent memory system to track user progress and avoid repetition
- Feedback-driven evaluation system for continuous improvement
- Tool-based architecture for modular and extensible design
- Streamlit cloud deployment for easy access (if deployed)

Architecture
The system is built around a modular multi-agent design with:
- specialized agents
- tool usage
- memory management
- iterative feedback loop
This allows the tutor to dynamically adapt to user inputs and learning behavior.

1. installation & Setup
Clone the repository
git clone https://github.com/YOUR_USERNAME/ai-adaptive-teacher.git
cd ai-adaptive-teacher

3. Install dependencies
pip install -r requirements.txt

API Key Configuration
This project requires an GEMINI LLM API key to run.
You can provide it in two ways:

Option 1 — Streamlit Secrets
Create a folder named: .streamlit
Inside it, create a file called: secrets.toml
Then add in the file: API_KEY = "YOUR_API_KEY"
Replace YOUR_API_KEY with your actual Gemini API key.

Option 2 — Direct input in the app
You can also enter your API key directly in the application interface.

Run the App
streamlit run app.py

Live Demo
If deployed on Streamlit Cloud:
[https://YOUR-STREAMLIT-APP-LINK](https://ai-adaptive-teacher-d5ahaxkuuygynx9isxcmey.streamlit.app/)

Technologies Used
Python
Streamlit
LLM API (OpenAI / Google / etc.)
Multi-agent architecture
Memory system
Prompt engineering



