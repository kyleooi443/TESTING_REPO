"""Build the single-file Minute Cat app with its artwork included."""

from pathlib import Path
from shutil import copy2
from tempfile import TemporaryDirectory
import zipapp


ROOT = Path(__file__).resolve().parent


def main():
    with TemporaryDirectory() as temporary:
        staging = Path(temporary)
        copy2(ROOT / "cat_reminder.py", staging / "cat_reminder.py")
        assets = staging / "assets"
        assets.mkdir()
        for filename in ("cats_walk_a.png", "cats_walk_b.png"):
            copy2(ROOT / "assets" / filename, assets / filename)
        (staging / "__main__.py").write_text("from cat_reminder import main\nmain()\n")
        zipapp.create_archive(
            staging,
            target=ROOT / "Minute-Cat.pyz",
            interpreter="/usr/bin/env python3",
            compressed=True,
        )


if __name__ == "__main__":
    main()
