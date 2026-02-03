import streamlit as st
import random
import time
from datetime import datetime

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
    accuracy = (
        st.session_state.score / st.session_state.total_attempts * 100
        if st.session_state.total_attempts > 0 else 0
    )

    total_time = time.time() - st.session_state.start_time

    with open("progress_log.txt", "a") as f:
        f.write("\n-----------------------------\n")
        f.write(f"Date: {datetime.now()}\n")
        f.write(f"Name: {st.session_state.player_name}\n")
        f.write(f"Score: {st.session_state.score}\n")
        f.write(f"Attempts: {st.session_state.total_attempts}\n")
        f.write(f"Accuracy: {accuracy:.2f}%\n")
        f.write(f"Time: {format_time(total_time)}\n")
        f.write(f"Max Number: {st.session_state.max_number}\n")
        f.write(f"Time Limit: {st.session_state.time_limit_minutes} minutes\n")

        if st.session_state.wrong_questions:
            f.write("Wrong Answers:\n")
            for q in st.session_state.wrong_questions:
                f.write(q + "\n")

# -----------------------------
# START SCREEN
# -----------------------------
if not st.session_state.game_started:

    st.title("Times Table Practice System")

    st.markdown("### Teacher Editable Text Below")
    st.markdown("You can customise instructions here.")

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
