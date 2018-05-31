from .action import CommentProcessingAction
from redditbotbuilder.util.praw import reddit_credentials_from_program_args
from .bot import RedditBot

class BotBuildingException(Exception):

    def __init__(self, msg):
        super().__init__(msg)

class RedditBotBuilder:

    def __init__(
            self,
            reddit,
            subreddits,
            *bot_args,
            _reddit_bot_constructor=RedditBot,
            _comment_processing_action_constructor=CommentProcessingAction,
            **bot_kwargs):
        self._reddit = reddit
        self._subreddits = subreddits
        self._comment_processing_actions = []
        self._bot_args = bot_args
        self._reddit_bot_constructor = _reddit_bot_constructor
        self._comment_processing_action_constructor = _comment_processing_action_constructor
        self._bot_kwargs = bot_kwargs

    def with_comment_processing(self, processing_fn):
        self._comment_processing_actions.append(self._comment_processing_action_constructor(processing_fn))
        return self

    def build(self):
        return self._reddit_bot_constructor(
            self._reddit,
            self._construct_activities_from_actions(),
            *self._bot_args,
            **self._bot_kwargs)

    def _construct_activities_from_actions(self):
        activities = []
        if not activities:
            raise BotBuildingException("No actions were provided for the bot to execute!")
        return activities

def of_program_args(
        *bot_builder_args,
        _bot_builder_constructor=RedditBotBuilder,
        _create_reddit_fn=reddit_credentials_from_program_args,
        **bot_builder_kwargs):
    """Creates a RedditBotBuilder with a PRAW Reddit instance that is instantiated from program args.

    # todo (example code + example command line invocation)

    :param bot_builder_args: other possible positional arguments to the bot builder, see `__init__()` for options.
    :param bot_builder_kwargs: same as `bot_builder_args`, just for keyword arguments.
    :returns: a RedditBotBuilder instance that uses a
    """
    return _bot_builder_constructor(_create_reddit_fn(), *bot_builder_args, **bot_builder_kwargs)
