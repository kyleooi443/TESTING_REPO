# Minute Cat

A cat walks across the bottom of your screen when the app starts and every minute after that. Each walk lasts about 10 seconds. The app cycles through an orange tabby, a tuxedo cat, a black cat, and a calico. Click **Next cat** to preview another, **Dismiss** to hide the current cat, or **Quit** to stop reminders. Press **Escape** to dismiss or **Q** to quit while the cat window has focus.

The cat is always on top. On Windows, the background is transparent; other desktops may show a small light background behind it.

Requires Python 3 with Tkinter and a graphical desktop. From this directory, run:

```sh
python3 cat_reminder.py
```

On Windows, use `py cat_reminder.py` instead. Keep the app running for the reminders to continue.

Run the timing test with:

```sh
python3 -m unittest -v
```
