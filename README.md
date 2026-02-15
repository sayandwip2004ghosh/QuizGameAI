# QuizGameAI
This project is an interactive Quiz Application built using Python with Tkinter GUI.
It loads questions from a JSON file, displays images when available, includes a countdown timer, sound feedback, category selection, scoreboard, and leaderboard saving, making it suitable for learning and practice quizzes.
The application aims to provide a visually engaging and easy-to-use education tool.
This project demonstrates how Python can be used to develop a graphical quiz program with features such as data loading, UI interactivity etc.
o	Display MCQ questions using a graphical interface
o	Load questions dynamically from JSON
o	Manage timer for each question
o	Save and load leaderboard records
o	Allow category-wise question selection and Shuffle questions randomly
SYSTEM REQUIREMENTS
Software Requirements
Requirement	Details
Programming Language	Python
Libraries	Tkinter, PIL, JSON, random, playsound
OS	Windows
Editor	VS Code / PyCharm / IDLE
                                                             	
   
SYSTEM DESIGN
Architecture Diagram
Questions.json → Python Quiz Engine → Tkinter GUI → User Responses → Score & Leaderboard

IMPLEMENTATION
Includes modules:
•	load_questions() – Reads JSON file
•	shuffle_questions() – Randomizes order
•	show_question() – Displays question, options, and image
•	start_timer() – Counts down time
•	check_answer() – Validates answers
•	save_score() – Writes score to leaderboard file
