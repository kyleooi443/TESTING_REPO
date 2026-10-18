"""A little desktop cat that takes a walk every minute."""

from dataclasses import dataclass
from itertools import cycle
from math import sin
from pathlib import Path
from time import monotonic
import base64
import sys
import tkinter as tk
from tkinter import ttk
import zipfile
import zipimport


MINUTE_MS = 60_000
FRAME_MS = 33
WALK_SECONDS = 10.0
BACKGROUND = "#fff5e9"
ASSET_DIR = Path(__file__).resolve().parent / "assets"
SPRITE_SIZE = 512


@dataclass(frozen=True)
class CatStyle:
    name: str
    cell: int


CAT_STYLES = (
    CatStyle("Orange tabby", 0),
    CatStyle("Tuxedo", 1),
    CatStyle("Black cat", 2),
    CatStyle("Calico", 3),
    CatStyle("Silver tabby", 4),
    CatStyle("Siamese", 5),
)


def artwork_bytes(filename):
    """Read artwork beside the source or from the standalone zip app."""
    path = ASSET_DIR / filename
    if path.is_file():
        return path.read_bytes()
    if isinstance(__loader__, zipimport.zipimporter):
        with zipfile.ZipFile(__loader__.archive) as bundle:
            try:
                return bundle.read(f"assets/{filename}")
            except KeyError:
                pass
    raise FileNotFoundError(
        "Cat artwork is missing. Extract the entire repository ZIP, including the assets "
        "folder, or run the standalone Minute-Cat.pyz file."
    )


def load_sprites(window):
    """Crop and scale the two transparent sheets with Tk's PNG support."""
    try:
        sheets = [
            tk.PhotoImage(master=window, data=base64.b64encode(artwork_bytes(filename)), format="png")
            for filename in ("cats_walk_a.png", "cats_walk_b.png")
        ]
    except tk.TclError as error:
        raise ValueError(f"Could not load cat artwork: {error}") from error
    if any(sheet.width() != 1536 or sheet.height() != 1024 for sheet in sheets):
        raise ValueError("Cat artwork has an unexpected size; download the full Minute Cat ZIP")
    sprites = {}
    for style in CAT_STYLES:
        x = (style.cell % 3) * SPRITE_SIZE
        y = (style.cell // 3) * SPRITE_SIZE
        frames = []
        for sheet in sheets:
            cropped = tk.PhotoImage(master=window, width=SPRITE_SIZE, height=SPRITE_SIZE)
            cropped.tk.call(
                str(cropped), "copy", str(sheet), "-from", x, y, x + SPRITE_SIZE, y + SPRITE_SIZE
            )
            frames.append(cropped.subsample(2, 2))
        sprites[style.name] = tuple(frames)
    return sprites


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
            self.cat_window, width=280, height=290, bg=BACKGROUND, highlightthickness=0
        )
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.pet_cat)
        self.cat_window.withdraw()

        try:
            self.sprites = load_sprites(self.window)
        except (FileNotFoundError, ValueError):
            self.window.destroy()
            raise
        self.styles = cycle(CAT_STYLES)
        self.current_style = None
        self.sprite_item = None
        self.sprite_frames = None
        self.current_pose = -1
        self.heart = None
        self.heart_job = None
        self.walk_job = None
        self.walk_started = 0.0
        self.timer = ReminderTimer(self.window.after, self.window.after_cancel, self.show_cat)
        self.timer.start()

    def draw_cat(self, style):
        canvas = self.canvas
        canvas.delete("all")
        self.sprite_frames = self.sprites[style.name]
        self.current_pose = 0
        self.sprite_item = canvas.create_image(140, 130, image=self.sprite_frames[0])
        canvas.create_text(140, 274, text=style.name, fill="#51413a", font=("TkDefaultFont", 12, "bold"))
        self.heart = canvas.create_text(
            100, 34, text="♥", fill="#e5788c", font=("TkDefaultFont", 26, "bold"), state="hidden"
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
        pose = int(elapsed * 6) % 2
        if pose != self.current_pose:
            self.canvas.itemconfigure(self.sprite_item, image=self.sprite_frames[pose])
            self.current_pose = pose
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


def main():
    try:
        CatReminder().run()
    except tk.TclError as error:
        show_startup_error(f"Minute Cat needs a graphical desktop: {error}")
    except (FileNotFoundError, ValueError) as error:
        show_startup_error(str(error))


def show_startup_error(message):
    print(message, file=sys.stderr)
    try:
        from tkinter import messagebox

        dialog = tk.Tk()
        dialog.withdraw()
        messagebox.showerror("Minute Cat", message, parent=dialog)
        dialog.destroy()
    except tk.TclError:
        pass


if __name__ == "__main__":
    main()
