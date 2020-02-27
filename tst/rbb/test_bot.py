from unittest.mock import Mock, call
import unittest
import pytest

from praw.models import Message, Comment, Submission
from rbb import RedditBot
from rbb.auth import AuthorisationMethod
from rbb.bot import ItemFilter, ItemProcessor, ItemDataProcessor, BotRunner
from rbb.lists import Blacklist

class RedditBotTest(unittest.TestCase):

    def test_run(self):
        reddit = Mock()
        username = "flerb"
        auth_provider = Mock()
        auth_provider.get_reddit = Mock(return_value=reddit)
        auth_provider.get_username = Mock(return_value=username)
        get_auth_provider = Mock(return_value=auth_provider)
        configure_logging = Mock()
        runner = Mock()
        runner_factory = Mock(return_value=runner)

        bot = RedditBot()
        bot.run(
            _get_auth_provider_fn=get_auth_provider,
            _bot_runner_factory_fn=runner_factory,
            _configure_logging_fn=configure_logging)
        
        """
        runner_factory.assert_called_with(
            reddit,
            bot,
            Blacklist("AutoModerator", "sub_corrector_bot"),
            Blacklist("suicidewatch", "depression"))
        """
        get_auth_provider.assert_called_with(AuthorisationMethod.PROGRAM_ARGS)
        configure_logging.assert_called_with(True, False, ".", username)
        runner.start_loop.assert_called_with()

class BotRunnerTest(unittest.TestCase):

    def setUp(self):
        self.first_comment = Mock()
        self.second_comment = Mock()
        self.reddit = Mock()
        self.reddit.inbox.unread = Mock(return_value=[self.first_comment, self.second_comment])
        self.item_processor = Mock()
        self.runner = BotRunner(self.reddit, self.item_processor)

        self.sleep = Mock()

    def test_start_loop_happy_case(self):
        self.start_loop()
        self.reddit.inbox.mark_read.assert_has_calls([
            call([self.first_comment]),
            call([self.second_comment])
        ])
        assert 2 == self.reddit.inbox.mark_read.call_count
        self.item_processor.process.assert_has_calls([
            call(self.first_comment),
            call(self.second_comment)
        ])
        assert 2 == self.item_processor.process.call_count

    def test_start_loop_exception_thrown(self):
        self.item_processor.process = Mock(side_effect=ValueError())
        self.start_loop()
        self.reddit.inbox.mark_read.assert_has_calls([
            call([self.first_comment])
        ])
        assert 1 == self.reddit.inbox.mark_read.call_count
        self.item_processor.process.assert_has_calls([
            call(self.first_comment)
        ])
        assert 1 == self.item_processor.process.call_count

    def start_loop(self):
        i = 0
        def loop_condition():
            nonlocal i
            if i == 0:
                i += 1
                return True
            return False
        self.runner.start_loop(
            _loop_condition=loop_condition,
            _sleep_fn=self.sleep)

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

    def mock_item(self, cls, text=None, **kwargs):
        if text is None:
            text = "blah blah u/" + self.bot_name.upper() + " BLAH BLAH"
        return mock_item(cls, text=text, **kwargs)

def mock_item(cls, author="someuser", sub="somesub", text="blah"):
    item = Mock(spec=cls)
    item.author = Mock()
    item.author.name = author
    item.subreddit = Mock()
    item.subreddit.display_name = sub
    item.body = text
    # possibly shouldn't set both here...
    # oh well.
    item.selftext = text
    return item
