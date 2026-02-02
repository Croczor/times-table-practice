import streamlit as st
import random
import time

# -----------------------------
# CONFIG
# -----------------------------
TIME_LIMIT = 10
TOTAL_QUESTIONS = 100
MIN_NUMBER = 1
MAX_NUMBER = 12
REFRESH_RATE = 0.1  # seconds

st.set_page_config(layout="centered")

# -----------------------------
# STYLING
# -----------------------------
st.markdown("""
<style>
div.block-container {
    text-align: center;
}
.stProgress > div > div > div > div {
    background-color: #00cc44;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# SESSION STATE DEFAULTS
# -----------------------------
defaults = {
    "game_started": False,
    "game_over": False,
    "score": 0,
    "question_number": 0,
    "total_attempts": 0,
    "correct_answer": 0,
    "start_time": 0.0,
    "total_start_time": 0.0,
    "question": "",
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# -----------------------------
# FUNCTIONS
# -----------------------------
def new_question():
    n1 = random.randint(MIN_NUMBER, MAX_NUMBER)
    n2 = random.randint(MIN_NUMBER, MAX_NUMBER)
    st.session_state.correct_answer = n1 * n2
    return f"{n1} × {n2}"

def start_game():
    st.session_state.game_started = True
    st.session_state.game_over = False
    st.session_state.score = 0
    st.session_state.question_number = 1
    st.session_state.total_attempts = 0
    st.session_state.total_start_time = time.time()
    st.session_state.start_time = time.time()
    st.session_state.question = new_question()

def end_game(reason):
    st.session_state.game_over = True
    st.session_state.reason = reason

def submit_answer():
    answer = st.session_state.answer_input

    if not answer:
        return

    try:
        user_answer = int(answer)
        st.session_state.total_attempts += 1

        if user_answer == st.session_state.correct_answer:
            st.session_state.score += 1

        if st.session_state.question_number >= TOTAL_QUESTIONS:
            end_game("Completed 100 Questions!")
            return

        st.session_state.question_number += 1
        st.session_state.question = new_question()
        st.session_state.start_time = time.time()

        st.session_state.answer_input = ""

    except ValueError:
        st.session_state.answer_input = ""

# -----------------------------
# START SCREEN
# -----------------------------
if not st.session_state.game_started:
    st.title("Times Table Practice")
    if st.button("Start Game"):
        start_game()
        st.rerun()

# -----------------------------
# GAME RUNNING
# -----------------------------
if st.session_state.game_started and not st.session_state.game_over:

    st.title("Times Table Practice")

    st.markdown(f"### Question {st.session_state.question_number} / {TOTAL_QUESTIONS}")
    st.markdown(f"## :yellow[{st.session_state.question} = ?]")

    # TIMER
    elapsed = time.time() - st.session_state.start_time
    remaining = TIME_LIMIT - elapsed

    if remaining <= 0:
        end_game("Time's Up!")
        st.rerun()

    progress = max(remaining / TIME_LIMIT, 0)
    st.progress(progress)

    st.markdown(f"**Time Remaining:** {remaining:.1f}s")

    total_elapsed = time.time() - st.session_state.total_start_time
    st.markdown(f"**Total Time:** {total_elapsed:.1f}s")

    st.text_input(
        "Your Answer",
        key="answer_input",
        on_change=submit_answer
    )

    # 🔥 AUTO REFRESH LOOP (THIS MAKES TIMER WORK)
    time.sleep(REFRESH_RATE)
    st.rerun()

# -----------------------------
# GAME OVER
# -----------------------------
if st.session_state.game_over:

    total_time = time.time() - st.session_state.total_start_time

    accuracy = (
        st.session_state.score / st.session_state.total_attempts * 100
        if st.session_state.total_attempts > 0 else 0
    )

    average_time = (
        total_time / st.session_state.total_attempts
        if st.session_state.total_attempts > 0 else 0
    )

    st.title("Game Over")
    st.markdown(f"### {st.session_state.reason}")
    st.markdown(f"**Score:** {st.session_state.score}")
    st.markdown(f"**Questions Attempted:** {st.session_state.total_attempts}")
    st.markdown(f"**Accuracy:** {accuracy:.2f}%")
    st.markdown(f"**Total Time:** {total_time:.2f}s")
    st.markdown(f"**Average Time per Question:** {average_time:.2f}s")

    if st.button("Play Again"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
