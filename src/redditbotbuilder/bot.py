import time

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