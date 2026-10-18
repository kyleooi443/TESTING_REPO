# Minute Cat

A cat walks across the bottom of your screen when the app starts and every minute after that. Each walk lasts about 10 seconds. The cats now use soft, realistic 3D-style artwork with two walking poses. Click a cat to show it some love.

![Six cat styles](assets/cats_walk_a.png)

The control window lets you preview a walk with **Show now**, **Pause** or **Resume** automatic walks, choose a specific cat, and **Quit** at any time. **Surprise me** rotates through six looks: orange tabby, tuxedo, black cat, calico, silver tabby, and Siamese. Keep the control window running for reminders to continue.

The walking cat stays on top. On Windows, its background is transparent; other desktops may show a small light background behind it.

## Download and run

**Windows:** [Download Minute-Cat.exe](https://raw.githubusercontent.com/kyleooi443/TESTING_REPO/main/Minute-Cat.exe), save it to your Downloads folder, and double-click it. No Python installation or ZIP extraction is needed. Keep the control window open for the cats to return every minute.

**macOS/Linux or Python users:** save the single [Minute-Cat.pyz](Minute-Cat.pyz) file and run `python3 Minute-Cat.pyz`. This version requires Python 3 with Tkinter and a graphical desktop. The artwork is inside the file.

If you download the repository ZIP instead, choose **Extract All** before opening `cat_reminder.py`. Keep the `assets` folder beside it. From the extracted directory, run:

```sh
python3 cat_reminder.py
```

On Windows, use the `.exe` above. If you run the source directly, Python 3 with Tkinter must be installed.

Run the timing test with:

```sh
python3 -m unittest -v
```

After changing the source or artwork, rebuild the standalone file with `python3 build_zipapp.py`.
