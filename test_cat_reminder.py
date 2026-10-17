import unittest

from cat_reminder import MINUTE_MS, ReminderTimer


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


if __name__ == "__main__":
    unittest.main()
