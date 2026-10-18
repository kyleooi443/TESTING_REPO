"""A little desktop cat that takes a walk every minute."""

from dataclasses import dataclass
from itertools import cycle
from math import pi, sin
from time import monotonic
import tkinter as tk
from tkinter import ttk


MINUTE_MS = 60_000
FRAME_MS = 33
WALK_SECONDS = 10.0
BACKGROUND = "#fff5e9"


@dataclass(frozen=True)
class CatStyle:
    name: str
    fur: str
    eyes: str
    pattern: str
    accent: str


CAT_STYLES = (
    CatStyle("Orange tabby", "#f3a856", "#3d6844", "tabby", "#b56b32"),
    CatStyle("Tuxedo", "#292d35", "#e4c34a", "tuxedo", "#f8f7ef"),
    CatStyle("Black cat", "#27272e", "#a9d96b", "plain", "#77747a"),
    CatStyle("Calico", "#f5e7cb", "#3d6844", "calico", "#df873f"),
    CatStyle("Silver tabby", "#8996a2", "#d8b862", "tabby", "#56636e"),
    CatStyle("Siamese", "#eadbc4", "#6a93b8", "siamese", "#65524b"),
)


def walk_x(progress, screen_width, window_width):
    """Move toward the cat's head, from the right edge to the left edge."""
    distance = max(0, screen_width - window_width)
    return round(distance * (1 - min(1, max(0, progress))))


class ReminderTimer:
    """Keep one reminder scheduled, with pause and manual preview controls."""

    def __init__(self, after, after_cancel, show):
        self.after = after
        self.after_cancel = after_cancel
        self.show = show
        self.job = None
        self.paused = False

    def start(self):
        self.show_now()

    def _schedule(self):
        if self.job is not None:
            self.after_cancel(self.job)
            self.job = None
        if not self.paused:
            self.job = self.after(MINUTE_MS, self._tick)

    def _tick(self):
        self.job = None
        self.show()
        self._schedule()

    def show_now(self):
        self.show()
        self._schedule()

    def toggle_pause(self):
        self.paused = not self.paused
        self._schedule()
        return self.paused


class CatReminder:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Minute Cat")
        self.window.resizable(False, False)
        self.window.configure(bg=BACKGROUND)
        self.window.protocol("WM_DELETE_WINDOW", self.window.destroy)
        theme = ttk.Style(self.window)
        theme.theme_use("clam")
        theme.configure("TFrame", background=BACKGROUND)
        theme.configure("TLabel", background=BACKGROUND, foreground="#51413a")
        theme.configure("TButton", padding=(9, 6), background="#f5c486", foreground="#51413a")
        theme.map("TButton", background=[("active", "#e9ae6c")])
        theme.configure("TCombobox", fieldbackground="#fffdf9")

        panel = ttk.Frame(self.window, padding=16)
        panel.grid()
        ttk.Label(panel, text="Minute Cat", font=("TkDefaultFont", 16, "bold")).grid(
            row=0, column=0, columnspan=3, sticky="w"
        )
        ttk.Label(panel, text="A tiny walk, every minute.").grid(row=1, column=0, columnspan=3, sticky="w", pady=(2, 12))
        ttk.Label(panel, text="Cat style").grid(row=2, column=0, sticky="w")
        self.style_name = tk.StringVar(value="Surprise me")
        ttk.Combobox(
            panel,
            textvariable=self.style_name,
            values=("Surprise me", *(style.name for style in CAT_STYLES)),
            state="readonly",
            width=19,
        ).grid(row=2, column=1, columnspan=2, sticky="ew", pady=6)
        self.status = tk.StringVar(value="Walking every minute")
        ttk.Label(panel, textvariable=self.status).grid(row=3, column=0, columnspan=3, sticky="w", pady=(4, 10))
        ttk.Button(panel, text="Show now", command=self.show_now).grid(row=4, column=0, padx=(0, 5))
        self.pause_button = ttk.Button(panel, text="Pause", command=self.toggle_pause)
        self.pause_button.grid(row=4, column=1, padx=5)
        ttk.Button(panel, text="Quit", command=self.window.destroy).grid(row=4, column=2, padx=(5, 0))
        self.window.geometry("+20+20")

        self.cat_window = tk.Toplevel(self.window)
        self.cat_window.overrideredirect(True)
        self.cat_window.protocol("WM_DELETE_WINDOW", self.hide_cat)
        self.cat_window.configure(bg=BACKGROUND)
        self.cat_window.attributes("-topmost", True)
        try:
            self.cat_window.attributes("-transparentcolor", BACKGROUND)
        except tk.TclError:
            pass  # Color transparency is available on some desktops, including Windows.
        self.canvas = tk.Canvas(
            self.cat_window, width=240, height=170, bg=BACKGROUND, highlightthickness=0
        )
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.pet_cat)
        self.cat_window.withdraw()

        self.styles = cycle(CAT_STYLES)
        self.current_style = None
        self.legs = []
        self.eyes = []
        self.tail = None
        self.heart = None
        self.heart_job = None
        self.walk_job = None
        self.walk_started = 0.0
        self.timer = ReminderTimer(self.window.after, self.window.after_cancel, self.show_cat)
        self.timer.start()

    def draw_cat(self, style):
        canvas = self.canvas
        canvas.delete("all")
        outline = "#51413a" if style.pattern != "plain" else "#77747a"
        canvas.create_oval(49, 130, 198, 144, fill="#d9cbbb", outline="")
        self.legs = [
            (canvas.create_line(x, 91, x, 126, fill=style.fur, width=12, capstyle="round"), x)
            for x in (88, 112, 146, 170)
        ]
        self.tail = canvas.create_line(
            165, 74, 192, 68, 211, 41, 216, 20,
            fill=style.fur, width=13, capstyle="round", smooth=True,
        )
        canvas.create_oval(67, 44, 183, 105, fill=style.fur, outline=outline, width=2)
        canvas.create_polygon(34, 51, 42, 10, 62, 39, fill=style.fur, outline=outline, width=2)
        canvas.create_polygon(70, 39, 88, 9, 96, 54, fill=style.fur, outline=outline, width=2)
        canvas.create_polygon(44, 23, 47, 35, 56, 35, fill="#df9298", outline="")
        canvas.create_polygon(82, 22, 77, 35, 88, 39, fill="#df9298", outline="")
        canvas.create_oval(27, 34, 103, 99, fill=style.fur, outline=outline, width=2)

        if style.pattern == "tabby":
            for x in (101, 125, 149):
                canvas.create_line(x, 49, x - 7, 67, fill=style.accent, width=4)
            for x in (55, 68, 81):
                canvas.create_line(x, 40, x, 51, fill=style.accent, width=3)
        elif style.pattern == "tuxedo":
            canvas.create_oval(76, 70, 127, 102, fill=style.accent, outline="")
            canvas.create_oval(40, 72, 83, 96, fill=style.accent, outline="")
        elif style.pattern == "calico":
            canvas.create_oval(95, 49, 133, 77, fill=style.accent, outline="")
            canvas.create_oval(144, 62, 177, 91, fill="#3a3539", outline="")
            canvas.create_oval(68, 37, 94, 59, fill=style.accent, outline="")
        elif style.pattern == "siamese":
            canvas.create_oval(36, 54, 92, 96, fill=style.accent, outline="")
            canvas.create_polygon(35, 49, 42, 11, 61, 39, fill=style.accent, outline="")
            canvas.create_polygon(70, 39, 88, 10, 96, 53, fill=style.accent, outline="")

        self.eyes = [
            (canvas.create_oval(x, 62, x + 8, 73, fill=style.eyes, outline=""), x)
            for x in (47, 77)
        ]
        canvas.create_polygon(61, 78, 71, 78, 66, 84, fill="#d78893", outline="")
        canvas.create_arc(56, 76, 66, 91, start=195, extent=135, style="arc", outline=outline, width=2)
        canvas.create_arc(66, 76, 76, 91, start=205, extent=135, style="arc", outline=outline, width=2)
        for end_y in (72, 84, 96):
            canvas.create_line(52, 83, 15, end_y, fill=outline, width=2)
            canvas.create_line(80, 83, 117, end_y, fill=outline, width=2)
        canvas.create_text(120, 156, text=style.name, fill="#51413a", font=("TkDefaultFont", 11, "bold"))
        self.heart = canvas.create_text(
            115, 22, text="♥", fill="#e5788c", font=("TkDefaultFont", 22, "bold"), state="hidden"
        )

    def show_cat(self):
        self.hide_cat()
        selected = self.style_name.get()
        self.current_style = next(self.styles) if selected == "Surprise me" else next(
            style for style in CAT_STYLES if style.name == selected
        )
        self.draw_cat(self.current_style)
        self.cat_window.update_idletasks()
        self.walk_started = monotonic()
        width = self.cat_window.winfo_reqwidth()
        height = self.cat_window.winfo_reqheight()
        start_x = walk_x(0, self.cat_window.winfo_screenwidth(), width)
        start_y = max(0, self.cat_window.winfo_screenheight() - height - 20)
        self.cat_window.geometry(f"+{start_x}+{start_y}")
        self.cat_window.deiconify()
        self.cat_window.lift()
        self.walk_frame()

    def walk_frame(self):
        self.walk_job = None
        elapsed = monotonic() - self.walk_started
        progress = min(1.0, elapsed / WALK_SECONDS)
        if progress >= 1.0:
            self.hide_cat()
            return
        width = self.cat_window.winfo_reqwidth()
        height = self.cat_window.winfo_reqheight()
        x = walk_x(progress, self.cat_window.winfo_screenwidth(), width)
        y = max(0, self.cat_window.winfo_screenheight() - height - 20) + round(abs(sin(elapsed * 14)) * 3)
        self.cat_window.geometry(f"+{x}+{y}")
        for index, (leg, base_x) in enumerate(self.legs):
            swing = round(sin(elapsed * 14 + (index % 2) * pi) * 9)
            self.canvas.coords(leg, base_x, 91, base_x + swing, 126)
        swish = sin(elapsed * 4) * 8
        self.canvas.coords(self.tail, 165, 74, 192, 68, 211, 41 + swish, 216, 20 + swish)
        blinking = elapsed > 0.5 and elapsed % 3.7 < 0.13
        for eye, eye_x in self.eyes:
            self.canvas.coords(eye, eye_x, 67 if blinking else 62, eye_x + 8, 69 if blinking else 73)
        self.walk_job = self.cat_window.after(FRAME_MS, self.walk_frame)

    def hide_cat(self):
        if self.walk_job is not None:
            self.cat_window.after_cancel(self.walk_job)
            self.walk_job = None
        if self.heart_job is not None:
            self.cat_window.after_cancel(self.heart_job)
            self.heart_job = None
        self.cat_window.withdraw()

    def pet_cat(self, event=None):
        if self.heart_job is not None:
            self.cat_window.after_cancel(self.heart_job)
        self.canvas.itemconfigure(self.heart, state="normal")

        def hide_heart():
            self.heart_job = None
            self.canvas.itemconfigure(self.heart, state="hidden")

        self.heart_job = self.cat_window.after(900, hide_heart)

    def show_now(self):
        self.timer.show_now()

    def toggle_pause(self):
        paused = self.timer.toggle_pause()
        if paused:
            self.hide_cat()
        self.pause_button.configure(text="Resume" if paused else "Pause")
        self.status.set("Paused — show a cat any time" if paused else "Walking every minute")

    def run(self):
        self.window.mainloop()


if __name__ == "__main__":
    try:
        CatReminder().run()
    except tk.TclError as error:
        raise SystemExit(f"Minute Cat needs a graphical desktop: {error}") from None
