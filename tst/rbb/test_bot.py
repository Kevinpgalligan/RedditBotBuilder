from unittest.mock import Mock, call
import pytest

from rbb.bot import RedditBot

class TestRedditBot:

    def test_run(self):
        reddit = Mock()
        reddit_factory = Mock(return_value=reddit)
        runner = Mock()
        runner_factory = Mock(return_value=runner)

        bot = RedditBot()
        bot.run(
            _reddit_factory_fn=reddit_factory,
            _bot_runner_factory_fn=runner_factory)
        
        runner_factory.assert_called_with(
            reddit,
            bot,
            set(["automoderator", "sub_corrector_bot"]),
            set(["suicidewatch", "depression"]))
        runner.start_loop.assert_called_with()
