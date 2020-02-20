from unittest.mock import Mock
import unittest
from praw.models import Comment, Submission, Message, Subreddit
from rbb.praw import is_post, has_author, author_name, subreddit_name, has_text, get_text, call_reddit_with_retries
import praw.exceptions
import time

def test_is_post():
    assert not is_post(None)
    assert not is_post(3)
    assert is_post(Mock(spec=Comment))
    assert is_post(Mock(spec=Submission))
    assert not is_post(Mock(spec=Message))

def test_has_author():
    assert not has_author(Mock(spec=Subreddit))
    mock_with_author = Mock()
    mock_with_author.author = "somePerson"
    assert has_author(mock_with_author)
    mock_with_none_as_author = Mock()
    mock_with_author.author = None
    assert has_author(mock_with_none_as_author)

def test_has_subreddit():
    assert not has_author(Mock(spec=Message))
    # here, relying on the fact that non-spec-based mocks
    # generate new mocks and return them when someone tries
    # to access an attribute.
    assert has_author(Mock())

class PrawTest(unittest.TestCase):
    def test_author_name_when_does_not_have_author(self):
        with self.assertRaises(ValueError):
            author_name(Mock(spec=Subreddit))

    def test_author_name_when_non_normalised_name(self):
        name = "BlahBlaHH"
        item = Mock()
        item.author.name = name
        assert name== author_name(item)

    def test_author_name_when_missing_name(self):
        item = Mock()
        item.author = None
        assert "[deleted]" == author_name(item)

    def test_subreddit_name_when_not_within_subreddit(self):
        with self.assertRaises(ValueError):
            subreddit_name(Mock(spec=Message))

    def test_subreddit_name_when_valid(self):
        item = Mock()
        item.subreddit.display_name = "BestSubredditEVER"
        assert "BestSubredditEVER" == subreddit_name(item)

    def test_get_text_when_submission(self):
        text = "sometext"
        s = Mock(spec=Submission)
        s.selftext = text
        assert text == get_text(s)

    def test_get_text_when_comment(self):
        text = "sometext"
        s = Mock(spec=Comment)
        s.body = text
        assert text == get_text(s)

    def test_get_text_when_does_not_have_any(self):
        with self.assertRaises(ValueError):
            get_text(Mock(spec=Subreddit))

def test_has_text():
    assert not has_text(Mock(spec=Subreddit))
    comment = Mock()
    comment.body = "blah"
    assert has_text(comment)
    sub = Mock()
    sub.selftext = "blah"
    assert has_text(sub)

class CallRedditTest(unittest.TestCase):

    def setUp(self):
        self.sleep_fn = Mock()

    def fn(self, e, num_times_to_raise=1):
        i = 0
        def reddit_calling_function():
            nonlocal i
            if i >= num_times_to_raise:
                return 0
            else:
                i += 1
                raise e
        return reddit_calling_function

    def call(self, e, num_times_to_raise=1):
        return call_reddit_with_retries(self.fn(e, num_times_to_raise), _sleep_fn=self.sleep_fn)

    def test_call_reddit_with_retries_when_unexpected_exception(self):
        with self.assertRaises(ValueError):
            self.call(ValueError())

    def test_call_reddit_with_retries_when_ratelimit_exception(self):
        assert 0 == self.call(praw.exceptions.APIException("RATELIMIT", "blah", None))
        self.sleep_fn.assert_called_with(10)

    def test_call_reddit_with_retries_when_apiexception_not_ratelimit(self):
        with self.assertRaises(praw.exceptions.APIException):
            self.call(praw.exceptions.APIException("not", "blah", None))

    def test_call_reddit_with_retries_when_network_exception(self):
        assert 0 == self.call(praw.exceptions.WebSocketException("blah", ValueError()))
        self.sleep_fn.assert_called_with(10)

    def test_call_reddit_with_retries_when_max_attempts_exceeded(self):
        with self.assertRaises(praw.exceptions.APIException):
            self.call(praw.exceptions.APIException("RATELIMIT", "blah", None), num_times_to_raise=4)
        assert 2 == self.sleep_fn.call_count
