from unittest.mock import Mock

import pytest

from redditbotbuilder.praw import create_reddit_from_program_args

CLIENT_ID = "client"
CLIENT_SECRET = "secret"
USER_AGENT = "v1.0 by jim"
USERNAME = "bob"
PASSWORD = "hunter2"

class TestPraw:

    def setup_method(self):
        self.expected_reddit = Mock()
        self.reddit_constructor = Mock(return_value=self.expected_reddit)

    def test_create_reddit_from_program_args_with_read_only(self):
        reddit = create_reddit_from_program_args(
            _reddit_constructor=self.reddit_constructor,
            _args=["script.py", CLIENT_ID, CLIENT_SECRET, USER_AGENT])

        assert self.expected_reddit == reddit
        self.reddit_constructor.assert_called_once_with(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, user_agent=USER_AGENT)

    def test_create_reddit_from_program_args_with_write_permissions(self):
        reddit = create_reddit_from_program_args(
            _reddit_constructor=self.reddit_constructor,
            _args=["script.py", CLIENT_ID, CLIENT_SECRET, USER_AGENT, USERNAME, PASSWORD])

        assert self.expected_reddit == reddit
        self.reddit_constructor.assert_called_once_with(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            user_agent=USER_AGENT,
            username=USERNAME,
            password=PASSWORD)

    def test_create_reddit_from_program_args_when_num_args_incorrect(self):
        with pytest.raises(ValueError):
            create_reddit_from_program_args(_reddit_constructor=self.reddit_constructor, _args=["scripy.py", CLIENT_ID])
