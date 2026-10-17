"""Send a different walking cat across the desktop once a minute."""

from dataclasses import dataclass
from itertools import cycle
import tkinter as tk


MINUTE_MS = 60_000
FRAME_MS = 40
WALK_FRAMES = 250  # Ten seconds at 40 ms per frame.
BACKGROUND = "#fff5e9"


@dataclass(frozen=True)
class CatStyle:
    name: str
    fur: str
    eyes: str
    pattern: str


CAT_STYLES = (
    CatStyle("Orange tabby", "#f3a856", "#3d6844", "tabby"),
    CatStyle("Tuxedo", "#292d35", "#e4c34a", "tuxedo"),
    CatStyle("Black cat", "#27272e", "#a9d96b", "plain"),
    CatStyle("Calico", "#f5e7cb", "#3d6844", "calico"),
)


def walk_x(frame, screen_width, window_width):
    """Move toward the cat's head, from the right edge to the left edge."""
    distance = max(0, screen_width - window_width)
    return distance - round(distance * frame / (WALK_FRAMES - 1))


class ReminderTimer:
    """Schedule reminders one minute apart, including one at startup."""

    def __init__(self, after, show):
        self.after = after
        self.show = show

    def start(self):
        self.show()
        self.after(MINUTE_MS, self.start)


class CatReminder:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Minute Cat")
        self.window.resizable(False, False)
        self.window.overrideredirect(True)
        self.window.configure(bg=BACKGROUND)
        self.window.attributes("-topmost", True)
        try:
            self.window.attributes("-transparentcolor", BACKGROUND)
        except tk.TclError:
            pass  # Tk only supports color transparency on some desktops.
        self.window.bind("<Escape>", lambda event: self.hide_cat())
        self.window.bind("q", lambda event: self.window.destroy())

        self.canvas = tk.Canvas(self.window, width=240, height=165, bg=BACKGROUND, highlightthickness=0)
        self.canvas.pack()
        controls = tk.Frame(self.window, bg=BACKGROUND)
        controls.pack(fill="x")
        for label, action in (
            ("Dismiss", self.hide_cat),
            ("Next cat", self.show_cat),
            ("Quit", self.window.destroy),
        ):
            tk.Button(controls, text=label, command=action).pack(side="left", expand=True, padx=3, pady=4)

        self.styles = cycle(CAT_STYLES)
        self.current_style = None
        self.legs = []
        self.frame = 0
        self.frame_job = None
        self.window.withdraw()
        ReminderTimer(self.window.after, self.show_cat).start()

    def draw_cat(self, style):
        canvas = self.canvas
        canvas.delete("all")
        outline = "#4b3b35" if style.pattern != "plain" else "#77747a"

        # Draw legs and tail first so the body covers their upper ends.
        self.legs = [
            (canvas.create_line(x, 91, x, 126, fill=style.fur, width=11, capstyle="round"), x)
            for x in (88, 112, 146, 170)
        ]
        canvas.create_arc(154, 16, 227, 103, start=295, extent=210, style="arc", outline=style.fur, width=13)
        canvas.create_oval(67, 44, 183, 105, fill=style.fur, outline=outline, width=2)
        canvas.create_polygon(34, 51, 42, 10, 62, 39, fill=style.fur, outline=outline, width=2)
        canvas.create_polygon(70, 39, 88, 9, 96, 54, fill=style.fur, outline=outline, width=2)
        canvas.create_oval(27, 34, 103, 99, fill=style.fur, outline=outline, width=2)

        if style.pattern == "tabby":
            for x in (101, 125, 149):
                canvas.create_line(x, 49, x - 7, 66, fill="#b56b32", width=4)
            canvas.create_line(56, 39, 55, 52, fill="#b56b32", width=3)
            canvas.create_line(69, 39, 70, 52, fill="#b56b32", width=3)
        elif style.pattern == "tuxedo":
            canvas.create_oval(76, 70, 127, 102, fill="#f8f7ef", outline="")
            canvas.create_oval(40, 72, 83, 96, fill="#f8f7ef", outline="")
        elif style.pattern == "calico":
            canvas.create_oval(95, 49, 133, 77, fill="#df873f", outline="")
            canvas.create_oval(144, 62, 177, 91, fill="#3a3539", outline="")
            canvas.create_oval(68, 37, 94, 59, fill="#df873f", outline="")

        canvas.create_oval(47, 62, 55, 73, fill=style.eyes, outline="")
        canvas.create_oval(77, 62, 85, 73, fill=style.eyes, outline="")
        canvas.create_polygon(61, 78, 71, 78, 66, 84, fill="#d78893", outline="")
        canvas.create_arc(56, 76, 66, 91, start=195, extent=135, style="arc", outline=outline, width=2)
        canvas.create_arc(66, 76, 76, 91, start=205, extent=135, style="arc", outline=outline, width=2)
        for end_y in (72, 84, 96):
            canvas.create_line(52, 83, 15, end_y, fill=outline, width=2)
            canvas.create_line(80, 83, 117, end_y, fill=outline, width=2)
        canvas.create_text(120, 151, text=style.name, fill="#4b3b35", font=("TkDefaultFont", 11, "bold"))

    def show_cat(self):
        self.hide_cat()
        self.current_style = next(self.styles)
        self.draw_cat(self.current_style)
        self.frame = 0
        self.window.update_idletasks()
        self.window.deiconify()
        self.window.lift()
        self.walk_frame()

    def walk_frame(self):
        self.frame_job = None
        if self.frame >= WALK_FRAMES:
            self.hide_cat()
            return

        width = self.window.winfo_reqwidth()
        height = self.window.winfo_reqheight()
        x = walk_x(self.frame, self.window.winfo_screenwidth(), width)
        stride = (self.frame // 5) % 2
        y = max(0, self.window.winfo_screenheight() - height - 20) + stride * 2
        self.window.geometry(f"+{x}+{y}")
        for index, (leg, base_x) in enumerate(self.legs):
            swing = 7 if (index + stride) % 2 == 0 else -7
            self.canvas.coords(leg, base_x, 91, base_x + swing, 126)

        self.frame += 1
        self.frame_job = self.window.after(FRAME_MS, self.walk_frame)

    def hide_cat(self):
        if self.frame_job is not None:
            self.window.after_cancel(self.frame_job)
            self.frame_job = None
        self.window.withdraw()

    def run(self):
        self.window.mainloop()


if __name__ == "__main__":
    try:
        CatReminder().run()
    except tk.TclError as error:
        raise SystemExit(f"Minute Cat needs a graphical desktop: {error}") from None
