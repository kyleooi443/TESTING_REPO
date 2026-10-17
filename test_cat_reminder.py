import unittest

from cat_reminder import CAT_STYLES, MINUTE_MS, WALK_FRAMES, ReminderTimer, walk_x


class ReminderTimerTests(unittest.TestCase):
    def test_shows_immediately_then_every_minute(self):
        scheduled = []
        shown = []
        timer = ReminderTimer(lambda delay, callback: scheduled.append((delay, callback)), lambda: shown.append(True))

        timer.start()
        self.assertEqual(len(shown), 1)
        self.assertEqual(scheduled[0][0], MINUTE_MS)

        scheduled.pop(0)[1]()
        self.assertEqual(len(shown), 2)
        self.assertEqual(scheduled[0][0], MINUTE_MS)

    def test_walks_toward_its_head(self):
        positions = [walk_x(frame, 1280, 240) for frame in range(WALK_FRAMES)]
        self.assertEqual(positions[0], 1040)
        self.assertEqual(positions[-1], 0)
        self.assertEqual(positions, sorted(positions, reverse=True))

    def test_cat_styles_are_distinct(self):
        self.assertEqual(len(CAT_STYLES), 4)
        self.assertEqual(len({style.name for style in CAT_STYLES}), 4)
        self.assertEqual(len({style.pattern for style in CAT_STYLES}), 4)


if __name__ == "__main__":
    unittest.main()
