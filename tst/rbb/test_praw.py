from unittest.mock import Mock
import unittest
from praw.models import Comment, Submission, Message, Subreddit
from rbb.praw import is_post, has_author, author_name, subreddit_name

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
        item = Mock()
        item.author = "BlahBlAA"
        assert "blahblaa" == author_name(item)

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
        assert "bestsubredditever" == subreddit_name(item)
