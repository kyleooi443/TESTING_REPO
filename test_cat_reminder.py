import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from zipfile import ZipFile

import cat_reminder
from cat_reminder import CAT_STYLES, MINUTE_MS, ReminderTimer, walk_x


class FakeClock:
    def __init__(self):
        self.jobs = {}
        self.next_id = 0

    def after(self, delay, callback):
        self.next_id += 1
        self.jobs[self.next_id] = (delay, callback)
        return self.next_id

    def cancel(self, job_id):
        del self.jobs[job_id]

    def fire(self):
        self.assert_one_job()
        job_id = next(iter(self.jobs))
        _, callback = self.jobs.pop(job_id)
        callback()

    def assert_one_job(self):
        assert len(self.jobs) == 1, self.jobs


class MinuteCatTests(unittest.TestCase):
    def test_missing_artwork_explains_how_to_run_the_app(self):
        with TemporaryDirectory() as temporary:
            with patch.object(cat_reminder, "ASSET_DIR", Path(temporary) / "missing"):
                with self.assertRaisesRegex(FileNotFoundError, "Extract the entire repository ZIP"):
                    cat_reminder.artwork_bytes("cats_walk_a.png")

    def test_standalone_app_contains_current_source_and_artwork(self):
        root = Path(__file__).resolve().parent
        with ZipFile(root / "Minute-Cat.pyz") as bundle:
            for name in ("cat_reminder.py", "assets/cats_walk_a.png", "assets/cats_walk_b.png"):
                bundled = bundle.read(name)
                source = (root / name).read_bytes()
                if name.endswith(".py"):
                    bundled = bundled.replace(b"\r\n", b"\n")
                    source = source.replace(b"\r\n", b"\n")
                self.assertEqual(bundled, source)

    def test_reminder_repeats_and_manual_show_resets_timer(self):
        clock = FakeClock()
        shown = []
        timer = ReminderTimer(clock.after, clock.cancel, lambda: shown.append(True))

        timer.start()
        self.assertEqual(len(shown), 1)
        self.assertEqual(next(iter(clock.jobs.values()))[0], MINUTE_MS)
        clock.fire()
        self.assertEqual(len(shown), 2)
        clock.assert_one_job()

        previous_job = next(iter(clock.jobs))
        timer.show_now()
        self.assertEqual(len(shown), 3)
        self.assertNotIn(previous_job, clock.jobs)
        clock.assert_one_job()

    def test_pause_stops_future_walks_but_allows_preview(self):
        clock = FakeClock()
        shown = []
        timer = ReminderTimer(clock.after, clock.cancel, lambda: shown.append(True))
        timer.start()

        self.assertTrue(timer.toggle_pause())
        self.assertEqual(clock.jobs, {})
        timer.show_now()
        self.assertEqual(len(shown), 2)
        self.assertEqual(clock.jobs, {})
        self.assertFalse(timer.toggle_pause())
        clock.assert_one_job()

    def test_cat_walks_toward_its_head(self):
        positions = [walk_x(step / 20, 1280, 240) for step in range(21)]
        self.assertEqual(positions[0], 1040)
        self.assertEqual(positions[-1], 0)
        self.assertEqual(positions, sorted(positions, reverse=True))

    def test_cat_styles_have_distinct_sprite_cells(self):
        self.assertEqual(len(CAT_STYLES), 6)
        self.assertEqual(len({style.name for style in CAT_STYLES}), 6)
        self.assertEqual({style.cell for style in CAT_STYLES}, set(range(6)))


if __name__ == "__main__":
    unittest.main()
