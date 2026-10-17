"""Show a small cat on the desktop once a minute."""

import tkinter as tk


MINUTE_MS = 60_000
VISIBLE_MS = 10_000


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
        self.window.attributes("-topmost", True)
        self.window.protocol("WM_DELETE_WINDOW", self.window.destroy)
        self.hide_job = None

        canvas = tk.Canvas(self.window, width=280, height=210, bg="#fff5e9", highlightthickness=0)
        canvas.pack()
        self.draw_cat(canvas)

        controls = tk.Frame(self.window, bg="#fff5e9")
        controls.pack(fill="x")
        tk.Button(controls, text="Dismiss", command=self.hide_cat).pack(side="left", padx=14, pady=12)
        tk.Button(controls, text="Quit", command=self.window.destroy).pack(side="right", padx=14, pady=12)

        self.window.withdraw()
        ReminderTimer(self.window.after, self.show_cat).start()

    @staticmethod
    def draw_cat(canvas):
        canvas.create_oval(89, 119, 205, 214, fill="#f3a856", outline="#5b3d2e", width=3)
        canvas.create_arc(174, 119, 265, 207, start=300, extent=225, style="arc", outline="#5b3d2e", width=8)
        canvas.create_polygon(72, 67, 89, 9, 129, 46, fill="#f3a856", outline="#5b3d2e", width=3)
        canvas.create_polygon(192, 67, 175, 9, 135, 46, fill="#f3a856", outline="#5b3d2e", width=3)
        canvas.create_polygon(89, 54, 94, 27, 114, 48, fill="#e58d90")
        canvas.create_polygon(175, 54, 170, 27, 150, 48, fill="#e58d90")
        canvas.create_oval(65, 33, 199, 155, fill="#f3a856", outline="#5b3d2e", width=3)
        canvas.create_oval(98, 86, 108, 101, fill="#322c2a", outline="")
        canvas.create_oval(156, 86, 166, 101, fill="#322c2a", outline="")
        canvas.create_polygon(126, 107, 138, 107, 132, 115, fill="#e58d90", outline="")
        canvas.create_arc(116, 105, 132, 126, start=190, extent=145, style="arc", outline="#5b3d2e", width=2)
        canvas.create_arc(132, 105, 148, 126, start=205, extent=145, style="arc", outline="#5b3d2e", width=2)
        for y, end_y in ((108, 100), (118, 118), (128, 136)):
            canvas.create_line(111, 117, 52, end_y, fill="#5b3d2e", width=2)
            canvas.create_line(153, 117, 212, end_y, fill="#5b3d2e", width=2)
        canvas.create_text(140, 190, text="Meow! Take a tiny break.", fill="#5b3d2e", font=("TkDefaultFont", 12, "bold"))

    def show_cat(self):
        if self.hide_job is not None:
            self.window.after_cancel(self.hide_job)
        self.window.update_idletasks()
        width = self.window.winfo_reqwidth()
        height = self.window.winfo_reqheight()
        self.window.geometry(
            f"{width}x{height}+{max(0, self.window.winfo_screenwidth() - width - 20)}"
            f"+{max(0, self.window.winfo_screenheight() - height - 20)}"
        )
        self.window.deiconify()
        self.window.lift()
        self.hide_job = self.window.after(VISIBLE_MS, self.hide_cat)

    def hide_cat(self):
        if self.hide_job is not None:
            self.window.after_cancel(self.hide_job)
            self.hide_job = None
        self.window.withdraw()

    def run(self):
        self.window.mainloop()


if __name__ == "__main__":
    try:
        CatReminder().run()
    except tk.TclError as error:
        raise SystemExit(f"Minute Cat needs a graphical desktop: {error}") from None
