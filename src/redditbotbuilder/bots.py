"""Tools to quickly build reddit bots.

The most convenient way to create a bot is to use the utility methods
that will return pre-configured bots. todo describe the types, show examples

The workhorse of the library is the `RedditBot` class, which
executes a collection of "activities" (such as scanning for comments,
replying to PMs, etc) either on a loop, or just once, depending on how
it is called.
"""

import time

from .activities import SubredditCommentScanningActivity
from .actions import CommentProcessingAction
from .praw import create_reddit_from_program_args

REDDIT_API_PULL_LIMIT = 100

class BotBuildingException(Exception):

    def __init__(self, msg):
        super().__init__(msg)

class RedditBotBuilder:

    @classmethod
    def of_program_args(cls, *args):
        """Creates a RedditBotBuilder with a PRAW Reddit instance that was instantiated using program args.

        """
        return RedditBotBuilder(create_reddit_from_program_args(), *args)

    @classmethod
    def of_credentials(cls):
        pass

    @classmethod
    def of_reddit(cls, reddit, *args):
        """Creates a RedditBotBuilder instance with directly-passed PRAW Reddit instance.

        :param reddit: a PRAW Reddit instance.
        :param args: other possible arguments to the bot builder, see `__init__()` for options.
        """
        return RedditBotBuilder(reddit, *args)

    def __init__(self, reddit, subreddits, *bot_args, **bot_kwargs):
        self._reddit = reddit
        self._subreddits = subreddits
        self._comment_processing_actions = []
        self._bot_args = bot_args
        self._bot_kwargs = bot_kwargs

    def with_comment_processing_action(self, processing_fn):
        self._comment_processing_actions.append(CommentProcessingAction(processing_fn))
        return self

    def build(self):
        activities = self._construct_activities_from_actions()
        return RedditBot(
            self._reddit,
            activities,
            *self._bot_args,
            **self._bot_kwargs)

    def _construct_activities_from_actions(self):
        activities = []
        if self._comment_processing_actions:
            activities.append(
                SubredditCommentScanningActivity(
                    self._reddit,
                    self._subreddits,
                    self._comment_processing_actions,
                    []))
        if not activities:
            raise BotBuildingException("No actions were provided for the bot to execute!")
        return activities

class RedditBot:
    """
    todo class docstring
    """

    DEFAULT_SECONDS_BETWEEN_RUNS = 60

    def __init__(
            self,
            reddit,
            activities,
            seconds_between_runs=DEFAULT_SECONDS_BETWEEN_RUNS,
            _sleep_fn=time.sleep,
            _loop_condition_fn=lambda: True):
        """Create a RedditBot instance.

        This involves instantiating an instance of PRAW's Reddit class using
        the provided credentials. If no credentials are provided, they will
        instead be read them from the command-line.

        todo mention that credentials arg should be tuple
        todo provide support for config files

        Here are the required credentials:

        * clientId: todo
        * clientSecret: todo
        * user-agent string: todo
        * [optional, needed only for bots with write permissions] botUsername
        * [optional, ^^^] botPassword

        If credentials are not passed to this constructor, you can pass them as CLI arguments like so:

            `python your-script.py clientId clientSecret userAgentString botUsername botPassword`

        This is the advised way to provide credentials, as you can then share your code without
        other people seeing them.

        :param reddit: an instance of PRAW's Reddit class.
        :param activities: the activities that the bot will execute in each loop,
            see `redditbotbuilder.activities`. todo explain what an activity is.
        :param seconds_between_runs: how many seconds to wait between each run of the bot when
            it is run on a loop.
        """
        # todo validate all args.
        self._reddit = reddit
        self._activities = activities
        self._seconds_between_runs = seconds_between_runs
        self._sleep_fn = _sleep_fn
        self._loop_condition_fn = _loop_condition_fn

    def run(self):
        """Run the bot at regular intervals.

        todo exception handling.

        :return: None
        """
        while self._loop_condition_fn():
            self.run_once()
            self._sleep_fn(self._seconds_between_runs)

    def run_once(self):
        """Run the bot for a single cycle.

        If one of the bot's activities fails (i.e. raises an exception), the
        other activities will still be executed. todo more detail on exception handling.

        :return: None
        """
        # todo catch exceptions
        # todo logging
        for activity in self._activities:
            activity.run()

def main():
    pass

if __name__ == "__main__":
    main()