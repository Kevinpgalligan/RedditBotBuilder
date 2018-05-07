from unittest.mock import Mock, call

import pytest

from redditbotbuilder.bot import RedditBot

class TestRedditBot:

    TIME_TO_SLEEP_IN_SECONDS = 100

    def setup_method(self, _):
        self.reddit = Mock()
        self.first_activity = Mock()
        self.second_activity = Mock()
        self.sleep_fn = Mock()
        self.loop_condition_fn = Mock(side_effect=[True, True, False])
        self.reddit = Mock()

        self.bot = RedditBot(
            self.reddit,
            [self.first_activity, self.second_activity],
            seconds_between_runs=TestRedditBot.TIME_TO_SLEEP_IN_SECONDS,
            _sleep_fn=self.sleep_fn,
            _loop_condition_fn=self.loop_condition_fn)

    def test_run_once(self):
        self.test_run_with(RedditBot.run_once, 1)

    def test_run(self):
        num_loops = 2

        self.test_run_with(RedditBot.run, num_loops)
        self.sleep_fn.assert_has_calls([call(TestRedditBot.TIME_TO_SLEEP_IN_SECONDS) for _ in range(num_loops)])

    @pytest.mark.skip(reason="this is a template for actual tests.")
    def test_run_with(self, run_fn, num_loops):
        expected_calls = [call() for _ in range(num_loops)]

        run_fn(self.bot)

        self.first_activity.run.assert_has_calls(expected_calls)
        self.second_activity.run.assert_has_calls(expected_calls)

