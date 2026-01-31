
import tkinter as tk
import random
import time

# ------------------------------
# Configuration
# ------------------------------
TIME_LIMIT = 3  # seconds per question
MIN_NUMBER = 0
MAX_NUMBER = 10
TOTAL_QUESTIONS = 100

BACKGROUND_COLOR = "#314378"
QUESTION_COLOR = "#FFE554"

BAR_WIDTH = 300
BAR_HEIGHT = 15


class TimesTableApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Times Table Practice")
        self.root.geometry("750x500")
        self.root.configure(bg=BACKGROUND_COLOR)

        # Game variables
        self.score = 0
        self.question_number = 0
        self.total_attempts = 0
        self.correct_answer = 0
        self.game_active = False
        self.start_time = None
        self.total_start_time = None

        # ------------------------------
        # UI Elements
        # ------------------------------
        self.question_label = tk.Label(
            root,
            text="",
            font=("Arial", 32),
            fg=QUESTION_COLOR,
            bg=BACKGROUND_COLOR
        )
        self.question_label.pack(pady=30)

        self.timer_label = tk.Label(
            root,
            text="",
            font=("Arial", 16),
            fg="white",
            bg=BACKGROUND_COLOR
        )
        self.timer_label.pack()

        self.canvas = tk.Canvas(
            root,
            width=BAR_WIDTH,
            height=BAR_HEIGHT,
            bg="white",
            highlightthickness=0
        )
        self.canvas.pack(pady=8)

        self.timer_bar = self.canvas.create_rectangle(
            0, 0, BAR_WIDTH, BAR_HEIGHT,
            fill="green"
        )

        self.answer_entry = tk.Entry(
            root,
            font=("Arial", 20)
        )
        self.answer_entry.pack(pady=20)
        self.answer_entry.bind("<Return>", self.check_answer)

        # Bottom info frame
        self.bottom_frame = tk.Frame(root, bg=BACKGROUND_COLOR)
        self.bottom_frame.pack(side="bottom", pady=20)

        self.counter_label = tk.Label(
            self.bottom_frame,
            text="0 / 100",
            font=("Arial", 14),
            fg="white",
            bg=BACKGROUND_COLOR
        )
        self.counter_label.pack()

        self.total_time_label = tk.Label(
            self.bottom_frame,
            text="Total Time: 0.0s",
            font=("Arial", 14),
            fg="white",
            bg=BACKGROUND_COLOR
        )
        self.total_time_label.pack()

        self.start_button = tk.Button(
            root,
            text="Start Game",
            font=("Arial", 16),
            command=self.start_game
        )
        self.start_button.pack(pady=20)

    # ------------------------------
    # Game Logic
    # ------------------------------
    def start_game(self):
        self.score = 0
        self.question_number = 0
        self.total_attempts = 0
        self.start_button.pack_forget()
        self.game_active = True
        self.total_start_time = time.time()
        self.next_question()
        self.update_total_time()

    def next_question(self):
        if self.question_number >= TOTAL_QUESTIONS:
            self.end_game("Completed 100 Questions!")
            return

        self.question_number += 1
        self.counter_label.config(text=f"{self.question_number} / {TOTAL_QUESTIONS}")

        num1 = random.randint(MIN_NUMBER, MAX_NUMBER)
        num2 = random.randint(MIN_NUMBER, MAX_NUMBER)
        self.correct_answer = num1 * num2

        self.question_label.config(text=f"{num1} × {num2} = ?")
        self.answer_entry.delete(0, tk.END)

        self.start_time = time.time()
        self.update_timer()

    def update_timer(self):
        if not self.game_active:
            return

        elapsed = time.time() - self.start_time
        remaining = TIME_LIMIT - elapsed

        if remaining <= 0:
            self.end_game("Time's Up!")
            return

        percent = remaining / TIME_LIMIT

        self.timer_label.config(text=f"Time left: {remaining:.1f}s")

        new_width = BAR_WIDTH * percent
        self.canvas.coords(self.timer_bar, 0, 0, new_width, BAR_HEIGHT)

        color = self.get_gradient_color(percent)
        self.canvas.itemconfig(self.timer_bar, fill=color)

        self.root.after(20, self.update_timer)

    def update_total_time(self):
        if not self.game_active:
            return

        total_elapsed = time.time() - self.total_start_time
        self.total_time_label.config(text=f"Total Time: {total_elapsed:.1f}s")

        self.root.after(100, self.update_total_time)

    # ------------------------------
    # Gradient Function
    # ------------------------------
    def get_gradient_color(self, percent):
        if percent > 0.5:
            ratio = (percent - 0.5) / 0.5
            r = int(255 * (1 - ratio))
            g = 255
        else:
            ratio = percent / 0.5
            r = 255
            g = int(255 * ratio)

        b = 0
        return f'#{r:02x}{g:02x}{b:02x}'

    def check_answer(self, event=None):
        if not self.game_active:
            return

        try:
            user_answer = int(self.answer_entry.get())
            self.total_attempts += 1

            if user_answer == self.correct_answer:
                self.score += 1

            self.next_question()

        except ValueError:
            pass  # ignore invalid input

    def end_game(self, reason):
        if not self.game_active:
            return

        self.game_active = False

        total_time = time.time() - self.total_start_time
        accuracy = (self.score / self.total_attempts * 100) if self.total_attempts > 0 else 0
        average_time = total_time / self.total_attempts if self.total_attempts > 0 else 0

        # Hide gameplay UI
        self.question_label.pack_forget()
        self.timer_label.pack_forget()
        self.canvas.pack_forget()
        self.answer_entry.pack_forget()
        self.bottom_frame.pack_forget()

        # Final Screen
        self.score_label = tk.Label(
            self.root,
            text=(
                f"{reason}\n\n"
                f"Score: {self.score}\n"
                f"Questions Attempted: {self.total_attempts}\n"
                f"Accuracy: {accuracy:.2f}%\n"
                f"Total Time: {total_time:.2f}s\n"
                f"Average Time per Question: {average_time:.2f}s"
            ),
            font=("Arial", 22),
            fg="white",
            bg=BACKGROUND_COLOR
        )
        self.score_label.pack(pady=60)

        self.restart_button = tk.Button(
            self.root,
            text="Play Again",
            font=("Arial", 16),
            command=self.restart_game
        )
        self.restart_button.pack()

    def restart_game(self):
        self.score_label.destroy()
        self.restart_button.destroy()

        self.question_label.pack(pady=30)
        self.timer_label.pack()
        self.canvas.pack(pady=8)
        self.answer_entry.pack(pady=20)
        self.bottom_frame.pack(side="bottom", pady=20)

        self.start_game()


# ------------------------------
# Run App
# ------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = TimesTableApp(root)
    root.mainloop()
