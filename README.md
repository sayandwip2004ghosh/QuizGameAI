# QuizGameAI
🧠 Interactive Quiz Application (Python + Tkinter)
📌 Project Overview

This project is an interactive Quiz Application developed using Python with a Tkinter-based GUI.
It loads questions dynamically from a JSON file, displays images when available, includes a countdown timer, provides sound feedback, supports category-wise quizzes, and maintains a scoreboard and leaderboard.

The application is designed to be visually engaging, easy to use, and suitable for learning, practice, and educational purposes.

🎯 Features

✅ Display MCQ questions using a graphical interface

✅ Load questions dynamically from a JSON file

✅ Category-wise question selection

✅ Shuffle questions randomly for better practice

✅ Countdown timer for each question

✅ Image support for questions

✅ Sound feedback for correct and incorrect answers

✅ Score calculation

✅ Save & load leaderboard records

🖥️ System Requirements
🔹 Software Requirements
Requirement	Details
Programming Language	Python
Libraries	Tkinter, PIL, JSON, random, playsound
Operating System	Windows
Code Editor	VS Code / PyCharm / IDLE
🏗️ System Design
🔹 Architecture Diagram (Flow)
Questions.json 
     ↓
Python Quiz Engine
     ↓
Tkinter GUI
     ↓
User Responses
     ↓
Score & Leaderboard

⚙️ Implementation Details
📂 Main Modules

load_questions()
→ Reads quiz questions from JSON file

shuffle_questions()
→ Randomizes question order

show_question()
→ Displays question, options, and image

start_timer()
→ Manages countdown timer

check_answer()
→ Validates user response

save_score()
→ Saves score to leaderboard file

🚀 How to Run the Project

Install required libraries:

pip install pillow playsound


Make sure questions.json is in the project directory

Run the Python file:

python quiz_app.py

📚 Learning Outcomes

Understanding GUI development using Tkinter

Working with JSON data files

Implementing timers and event handling

Managing file-based leaderboard storage

Building a complete interactive desktop application

🤝 Contribution

Contributions are welcome!
Feel free to fork this repository and submit a pull request.
