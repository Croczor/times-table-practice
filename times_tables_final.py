import streamlit as st
import random
import time
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(layout="centered")

# -----------------------------
# CUSTOM STYLING
# -----------------------------
st.markdown("""
<style>
html, body, [class*="css"]  {
    background-color: #2f3e4e;
    color: white;
}
div.block-container {
    text-align: center;
}
.stProgress > div > div > div > div {
    background-color: #00cc44;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# DEFAULT SESSION STATE
# -----------------------------
defaults = {
    "game_started": False,
    "game_over": False,
    "score": 0,
    "question_number": 0,
    "total_attempts": 0,
    "wrong_questions": [],
    "correct_answer": 0,
    "start_time": 0.0,
    "question": "",
    "max_number": 12,
    "total_questions": 100,
    "time_limit_minutes": 5,
    "player_name": ""
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# -----------------------------
# FUNCTIONS
# -----------------------------
def format_time(seconds):
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"

def new_question():
    n1 = random.randint(1, st.session_state.max_number)
    n2 = random.randint(1, st.session_state.max_number)
    st.session_state.correct_answer = n1 * n2
    return f"{n1} × {n2}"

def start_game():

    if not st.session_state.player_name.strip():
        st.warning("Please enter your name before starting.")
        return
    
    st.session_state.game_started = True
    st.session_state.game_over = False
    st.session_state.score = 0
    st.session_state.question_number = 1
    st.session_state.total_attempts = 0
    st.session_state.wrong_questions = []
    st.session_state.start_time = time.time()
    st.session_state.question = new_question()

def end_game(reason):
    st.session_state.game_over = True
    st.session_state.reason = reason
    save_progress()

def submit_answer():
    answer = st.session_state.answer_input
    if not answer:
        return
    try:
        user_answer = int(answer)
        st.session_state.total_attempts += 1

        if user_answer == st.session_state.correct_answer:
            st.session_state.score += 1
        else:
            st.session_state.wrong_questions.append(
                f"{st.session_state.question} = {user_answer} (Correct: {st.session_state.correct_answer})"
            )

        if st.session_state.question_number >= st.session_state.total_questions:
            end_game("Completed Question Goal")
            return

        st.session_state.question_number += 1
        st.session_state.question = new_question()
        st.session_state.answer_input = ""

    except ValueError:
        st.session_state.answer_input = ""

def save_progress():

    import pytz

    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scope
    )

    client = gspread.authorize(creds)

    sheet = client.open_by_key(
        "1co5kojLIbT4zYpIGQo6hgJLypN5gCQ4mII4Y9TnQgsE"
    ).sheet1

    # -------------------------
    # AEST DATE/TIME
    # -------------------------
    aest = pytz.timezone("Australia/Brisbane")
    now = datetime.now(aest)
    formatted_time = now.strftime("%d/%m/%Y %H:%M:%S")

    # -------------------------
    # ELAPSED TIME (mm:ss)
    # -------------------------
    total_seconds = int(time.time() - st.session_state.start_time)
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    time_string = f"{minutes:02}:{seconds:02}"

    # -------------------------
    # ACCURACY
    # -------------------------
    if st.session_state.total_attempts > 0:
        accuracy = (
            st.session_state.score /
            st.session_state.total_attempts
        ) * 100
    else:
        accuracy = 0

    # -------------------------
    # WRONG ANSWERS STRING
    # -------------------------
    if st.session_state.wrong_questions:
        wrong_string = " | ".join(st.session_state.wrong_questions)
    else:
        wrong_string = "None"

    # -------------------------
    # CALCULATE ATTEMPT NUMBER
    # -------------------------
    student_name = st.session_state.player_name

    # Get existing names in column B (Student column)
    existing_students = sheet.col_values(2)[2:]  # skip first two rows

    attempt_number = existing_students.count(student_name) + 1

    # -------------------------
    # FINAL ROW STRUCTURE
    # -------------------------
    row_data = [
        student_name,                     # Student
        f"Attempt {attempt_number}",      # Attempt
        formatted_time,                   # Date
        st.session_state.score,           # Score
        st.session_state.total_questions, # MaxQuestions
        f"{accuracy:.2f}%",               # Accuracy
        time_string,                      # Time
        st.session_state.max_number,      # MaxNumber
        st.session_state.time_limit_minutes, # TimeLimit
        wrong_string                      # WrongAnswers
    ]

    sheet.append_row(row_data, table_range="B3")


# -----------------------------
# START SCREEN
# -----------------------------

if not st.session_state.game_started:

    st.title("Times Table Practice System")

    st.markdown("### Please enter your name below:")
    st.markdown("Please use the naming scheme: Year level, First name initial, Last name first three letters. E.g., 7JSMI for John Smith in year 7.")

    st.text_input("Student Name:", key="player_name")

    st.session_state.max_number = st.slider(
        "Maximum Multiplication Number",
        5, 20, 12
    )

    st.session_state.total_questions = st.slider(
        "Total Questions",
        10, 200, 100
    )

    st.session_state.time_limit_minutes = st.slider(
        "Time Limit (Minutes)",
        1, 10, 5
    )

    if st.button("Start Game"):
        start_game()
        st.rerun()

# -----------------------------
# GAME RUNNING
# -----------------------------
else:
    if st.session_state.game_started and not st.session_state.game_over:
    
        st.title("Times Table Practice")
    
        elapsed = time.time() - st.session_state.start_time
        total_limit_seconds = st.session_state.time_limit_minutes * 60
        remaining = total_limit_seconds - elapsed
    
        if remaining <= 0:
            end_game("Time Expired")
            st.rerun()
    
        progress = max(remaining / total_limit_seconds, 0)
        st.progress(progress)
    
        st.markdown(f"### Time Remaining: {format_time(remaining)}")
        st.markdown(f"### Question {st.session_state.question_number} / {st.session_state.total_questions}")
        st.markdown(f"## :yellow[{st.session_state.question} = ?]")
    
        st.text_input("Your Answer", key="answer_input", on_change=submit_answer)
    
        time.sleep(0.1)
        st.rerun()

# -----------------------------
# GAME OVER SCREEN
# -----------------------------
if st.session_state.game_over:

    total_time = time.time() - st.session_state.start_time
    accuracy = (
        st.session_state.score / st.session_state.total_attempts * 100
        if st.session_state.total_attempts > 0 else 0
    )

    # Performance Colour
    if accuracy >= 90:
        color = "#00ff88"
    elif accuracy >= 70:
        color = "#ffe066"
    else:
        color = "#ff4d4d"

    st.markdown(f"<h1 style='color:{color};'>Game Over</h1>", unsafe_allow_html=True)

    st.markdown(f"### Score: {st.session_state.score}")
    st.markdown(f"### Accuracy: {accuracy:.2f}%")
    st.markdown(f"### Time Played: {format_time(total_time)}")

    if st.session_state.wrong_questions:
        st.markdown("### Wrong Answers:")
        for q in st.session_state.wrong_questions:
            st.write(q)

    if st.button("Play Again"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()



















