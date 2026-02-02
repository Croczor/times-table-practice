
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

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(layout="centered")

# Custom CSS to center everything + green progress bar
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
# SESSION STATE INIT
# -----------------------------
if "game_started" not in st.session_state:
    st.session_state.game_started = False
    st.session_state.game_over = False
    st.session_state.score = 0
    st.session_state.question_number = 0
    st.session_state.total_attempts = 0
    st.session_state.correct_answer = 0
    st.session_state.start_time = None
    st.session_state.total_start_time = None

# -----------------------------
# FUNCTIONS
# -----------------------------
def new_question():
    num1 = random.randint(MIN_NUMBER, MAX_NUMBER)
    num2 = random.randint(MIN_NUMBER, MAX_NUMBER)
    st.session_state.correct_answer = num1 * num2
    return f"{num1} × {num2}"

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

    # Question counter
    st.markdown(f"### Question {st.session_state.question_number} / {TOTAL_QUESTIONS}")

    # Show question
    st.markdown(f"## :yellow[{st.session_state.question} = ?]")

    # Timer logic
    elapsed = time.time() - st.session_state.start_time
    remaining = TIME_LIMIT - elapsed

    if remaining <= 0:
        end_game("Time's Up!")
        st.rerun()

    progress = max(remaining / TIME_LIMIT, 0)
    st.progress(progress)

    st.markdown(f"**Time Remaining:** {remaining:.1f}s")

    # Total time
    total_elapsed = time.time() - st.session_state.total_start_time
    st.markdown(f"**Total Time:** {total_elapsed:.1f}s")

    # Answer input
    answer = st.text_input("Your Answer", key="answer")

    if answer:
        try:
            user_answer = int(answer)
            st.session_state.total_attempts += 1

            if user_answer == st.session_state.correct_answer:
                st.session_state.score += 1

            if st.session_state.question_number >= TOTAL_QUESTIONS:
                end_game("Completed 100 Questions!")
            else:
                st.session_state.question_number += 1
                st.session_state.question = new_question()
                st.session_state.start_time = time.time()

            st.session_state.answer = ""
            st.rerun()

        except ValueError:
            st.session_state.answer = ""

# -----------------------------
# GAME OVER SCREEN
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
