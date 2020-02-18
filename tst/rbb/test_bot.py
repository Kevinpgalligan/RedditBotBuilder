from unittest.mock import Mock, call
import unittest
import pytest

from praw.models import Message, Comment, Submission
from rbb.bot import RedditBot, ItemFilter, ItemProcessor
from rbb.lists import Blacklist

class RedditBotTest(unittest.TestCase):

    def test_run(self):
        reddit = Mock()
        reddit_factory = Mock(return_value=reddit)
        runner = Mock()
        runner_factory = Mock(return_value=runner)

        bot = RedditBot()
        bot.run(
            _reddit_factory_fn=reddit_factory,
            _bot_runner_factory_fn=runner_factory)
        
        """
        runner_factory.assert_called_with(
            reddit,
            bot,
            Blacklist("AutoModerator", "sub_corrector_bot"),
            Blacklist("suicidewatch", "depression"))
        """
        runner.start_loop.assert_called_with()

class ItemProcessorTest(unittest.TestCase):

    def test_process_when_item_passes_filter(self):
        f = Mock()
        f.should_process_data = Mock(return_value=True)
        data_processor = Mock()
        p = ItemProcessor(f, data_processor)
        item = Mock()
        p.process(item)
        data_processor.process.assert_called_with(item)
        
    def test_process_when_item_fails_filter(self):
        f = Mock()
        f.should_process_data = Mock(return_value=False)
        data_processor = Mock()
        p = ItemProcessor(f, data_processor)
        item = Mock()
        p.process(item)
        assert not data_processor.should_process_data.called

class ItemFilterTest(unittest.TestCase):
    
    def setUp(self):
        self.bot_name = "somebot"
        self.f = ItemFilter(
            self.bot_name,
            Blacklist("automoderator"),
            Blacklist("suicidewatch"))

    def test_should_process_data_when_unsupported_type(self):
        assert not self.f.should_process_data(Mock(spec=Message))

    def test_should_process_data_when_author_blacklisted(self):
        assert not self.f.should_process_data(self.mock_comment(author="AutoModerator"))

    def test_should_process_data_when_subreddit_blacklisted(self):
        assert not self.f.should_process_data(self.mock_comment(sub="SuicideWatch"))

    def test_should_process_data_when_not_tagged(self):
        assert not self.f.should_process_data(self.mock_comment(text="not tagged here"))

    def test_should_process_data_when_comment_passes_filters(self):
        assert self.f.should_process_data(self.mock_comment())

    def test_should_process_data_when_submission_passes_filters(self):
        assert self.f.should_process_data(self.mock_item(Submission))

    def mock_comment(self, **kwargs):
        return self.mock_item(Comment, **kwargs)

    def mock_item(self, cls, author="someuser", sub="somesub", text=None):
        if text is None:
            text = "blah blah " + self.bot_name.upper() + " BLAH BLAH"
        item = Mock(spec=cls)
        item.author = author
        item.subreddit = Mock()
        item.subreddit.display_name = sub
        item.body = Mock()
        item.body = text
        return item
