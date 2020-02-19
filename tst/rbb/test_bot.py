from unittest.mock import Mock, call
import unittest
import pytest

from praw.models import Message, Comment, Submission
from rbb import RedditBot
from rbb.bot import ItemFilter, ItemProcessor, ItemDataProcessor
from rbb.lists import Blacklist

class RedditBotTest(unittest.TestCase):

    def test_run(self):
        reddit = Mock()
        me = Mock()
        me.name = "somebot"
        reddit.user.me = Mock(return_value=me)
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

    def mock_item(self, cls, text=None, **kwargs):
        if text is None:
            text = "blah blah u/" + self.bot_name.upper() + " BLAH BLAH"
        return mock_item(cls, text=text, **kwargs)
    
class ItemDataProcessorTest(unittest.TestCase):

    def setUp(self):
        self.comment = mock_item(Comment)
        self.parent = mock_item(Comment, author="otheruser", text="parenttext")
        self.comment.parent = Mock(return_value=self.parent)
    
    def test_process_when_no_methods_implemented(self):
        # TODO make this more general... when new methods are added,
        # it will be easy to forget to add them here.
        bot = RedditBot()
        processor = ItemDataProcessor(bot)
        processor.process(self.comment)
        assert not self.comment.reply.called
        assert not self.comment.parent.called

    def test_process_when_methods_implemented(self):
        # TODO make this more general... when new methods are added,
        # it will be easy to forget to add them here.
        reply = "hi"
        parent_reply = "hi parent"
        bot = Mock(spec=Comment)
        bot.reply_using_parent_of_mention = Mock(return_value=parent_reply, spec=[])
        bot.reply_to_mention = Mock(return_value=reply, spec=[])
        bot.process_mention = Mock(spec=[])
        processor = ItemDataProcessor(bot)

        processor.process(self.comment)
        
        bot.reply_using_parent_of_mention.assert_called_with(self.parent.author.name, self.parent.body)
        bot.reply_to_mention.assert_called_with(self.comment.author.name, self.comment.body)
        assert bot.process_mention.called
        self.comment.reply.has_calls(
            call(reply),
            call(parent_reply))
        

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
