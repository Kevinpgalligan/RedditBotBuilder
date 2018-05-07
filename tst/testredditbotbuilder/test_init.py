from unittest.mock import Mock

import pytest

from redditbotbuilder import of_program_args
from redditbotbuilder import RedditBotBuilder
from redditbotbuilder import BotBuildingException

class TestCreationFunctions:

    def setup_method(self, _):
        self.reddit = Mock()
        self.create_reddit_fn = Mock(return_value=self.reddit)
        self.bot_builder = Mock()
        self.bot_builder_constructor = Mock(return_value=self.bot_builder)

    def test_of_program_args(self):
        positional_arg = Mock()
        keyword_arg = Mock()

        builder = of_program_args(
            positional_arg,
            _bot_builder_constructor=self.bot_builder_constructor,
            _create_reddit_fn=self.create_reddit_fn,
            keyword_arg=keyword_arg)

        self.create_reddit_fn.assert_called_once_with()
        self.bot_builder_constructor.assert_called_once_with(self.reddit, positional_arg, keyword_arg=keyword_arg)
        assert self.bot_builder == builder

class TestRedditBotBuilder:

    SUBREDDITS = "hello+world"

    def setup_method(self, _):
        self.reddit = Mock()
        self.positional_arg = Mock()
        self.keyword_arg = Mock()
        self.reddit_bot = Mock()
        self.reddit_bot_constructor = Mock(return_value=self.reddit_bot)
        self.comment_processing_action = Mock()
        self.comment_processing_action_constructor = Mock(return_value=self.comment_processing_action)
        self.comment_scanning_activity = Mock()
        self.comment_scanning_activity_constructor = Mock(return_value=self.comment_scanning_activity)
        self.builder = RedditBotBuilder(
            self.reddit,
            TestRedditBotBuilder.SUBREDDITS,
            self.positional_arg,
            _reddit_bot_constructor=self.reddit_bot_constructor,
            _comment_processing_action_constructor=self.comment_processing_action_constructor,
            _comment_scanning_activity_constructor=self.comment_scanning_activity_constructor,
            keyword_arg=self.keyword_arg)

    def test_build_without_adding_any_actions(self):
        with pytest.raises(BotBuildingException):
            self.builder.build()

    def test_build_with_comment_processing(self):
        processing_fn = Mock()

        bot = self.builder\
            .with_comment_processing(processing_fn)\
            .build()

        self.comment_processing_action_constructor.assert_called_once_with(processing_fn)
        self.comment_scanning_activity_constructor.assert_called_once_with(
            self.reddit,
            TestRedditBotBuilder.SUBREDDITS,
            [self.comment_processing_action],
            [])
        self.reddit_bot_constructor.assert_called_once_with(
            self.reddit,
            [self.comment_scanning_activity],
            self.positional_arg,
            keyword_arg=self.keyword_arg)
        assert self.reddit_bot == bot
