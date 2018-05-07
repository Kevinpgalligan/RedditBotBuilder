from .activities import SubredditCommentScanningActivity
from .actions import CommentProcessingAction
from .praw import create_reddit_from_program_args
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
            _comment_scanning_activity_constructor=SubredditCommentScanningActivity,
            **bot_kwargs):
        self._reddit = reddit
        self._subreddits = subreddits
        self._comment_processing_actions = []
        self._bot_args = bot_args
        self._reddit_bot_constructor = _reddit_bot_constructor
        self._comment_processing_action_constructor = _comment_processing_action_constructor
        self._comment_scanning_activity_constructor = _comment_scanning_activity_constructor
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
        if self._comment_processing_actions:
            activities.append(
                self._comment_scanning_activity_constructor(
                    self._reddit,
                    self._subreddits,
                    self._comment_processing_actions,
                    []))
        if not activities:
            raise BotBuildingException("No actions were provided for the bot to execute!")
        return activities

def of_program_args(
        *bot_args,
        _bot_builder_constructor=RedditBotBuilder,
        _create_reddit_fn=create_reddit_from_program_args,
        **bot_kwargs):
    """Creates a RedditBotBuilder with a PRAW Reddit instance that is instantiated from program args.

    """
    return _bot_builder_constructor(_create_reddit_fn(), *bot_args, **bot_kwargs)

def of_credentials():
    pass

def of_reddit(reddit, *bot_args, **bot_kwargs):
    """Creates a RedditBotBuilder instance with directly-passed PRAW Reddit instance.

    :param reddit: a PRAW Reddit instance.
    :param bot_args: other possible positional arguments to the bot builder, see `__init__()` for options.
    :param bot_kwargs: same as `bot_args`, just for keyword arguments.
    """
    return RedditBotBuilder(reddit, *bot_args, **bot_kwargs)
