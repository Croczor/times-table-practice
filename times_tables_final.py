
import streamlit as st
import random
import time

# ------------------------------
# Configuration
# ------------------------------
TIME_LIMIT = 10
TOTAL_QUESTIONS = 100
MIN_NUMBER = 1
MAX_NUMBER = 12

# ------------------------------
# Session State Setup
# ------------------------------
if "started" not in st.session_state:
    st.session_state.started = False
    st.session_state.score = 0
    st.session_state.question_number = 0
    st.session_state.total_attempts = 0
    st.session_state.start_time = 0
    st.session_state.total_start_time = 0
    st.session_state.correct_answer = 0
    st.session_state.game_over = False

# ------------------------------
# Helper Functions
# ------------------------------
def generate_question():
    num1 = random.randint(MIN_NUMBER, MAX_NUMBER)
    num2 = random.randint(MIN_NUMBER, MAX_NUMBER)
    st.session_state.correct_answer = num1 * num2
    return f"{num1} × {num2}"

def end_game(reason):
    st.session_state.game_over = True
    st.session_state.reason = reason


# ------------------------------
# UI
# ------------------------------
st.title("Times Table Practice")

if not st.session_state.started:
    if st.button("Start Game"):
        st.session_state.started = True
        st.session_state.score = 0
        st.session_state.question_number = 0
        st.session_state.total_attempts = 0
        st.session_state.total_start_time = time.time()
        st.session_state.question = generate_question()

# ------------------------------
# Game Running
# ------------------------------
if st.session_state.started and not st.session_state.game_over:

    # Question Counter
    st.write(f"### Question {st.session_state.question_number + 1} / {TOTAL_QUESTIONS}")

    # Show Question
    st.markdown(f"## :yellow[{st.session_state.question} = ?]")

    # Timer
    elapsed = time.time() - st.session_state.start_time if st.session_state.start_time else 0
    remaining = TIME_LIMIT - elapsed

    if remaining <= 0:
        end_game("Time's Up!")

    progress = remaining / TIME_LIMIT
    if progress < 0:
        progress = 0

    st.progress(progress)

    # Total Time Display
    total_elapsed = time.time() - st.session_state.total_start_time
    st.write(f"Total Time: {total_elapsed:.2f}s")

    # Answer Input
    answer = st.text_input("Your Answer", key="answer_input")

    if answer:
        try:
            user_answer = int(answer)
            st.session_state.total_attempts += 1

            if user_answer == st.session_state.correct_answer:
                st.session_state.score += 1

            st.session_state.question_number += 1

            if st.session_state.question_number >= TOTAL_QUESTIONS:
                end_game("Completed 100 Questions!")
            else:
                st.session_state.question = generate_question()
                st.session_state.start_time = time.time()

            st.rerun()

        except ValueError:
            pass

# ------------------------------
# End Screen
# ------------------------------
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

    st.success("Game Over!")
    st.write(f"Reason: {st.session_state.reason}")
    st.write(f"Score: {st.session_state.score}")
    st.write(f"Questions Attempted: {st.session_state.total_attempts}")
    st.write(f"Accuracy: {accuracy:.2f}%")
    st.write(f"Total Time: {total_time:.2f}s")
    st.write(f"Average Time per Question: {average_time:.2f}s")

    if st.button("Restart"):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()
