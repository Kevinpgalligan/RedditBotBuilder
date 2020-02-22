import rbb.auth
from rbb.praw import normalise, call_reddit_with_retries
from rbb.bot import BotRunner, ItemProcessor, ItemFilter, ItemDataProcessor
from rbb.lists import BASE_USER_BLACKLIST, BASE_SUBREDDIT_BLACKLIST
from rbb.interfaces import unimplemented
import rbb.logging
from rbb.logging import log_info

class RedditBot:

    def run(
            self,
            log_to_console=True,
            log_to_file=False,
            log_dir=".",
            _reddit_factory_fn=rbb.auth.reddit_from_program_args,
            _bot_runner_factory_fn=BotRunner,
            _log_config_fn=rbb.logging.configure):
        reddit = _reddit_factory_fn()
        # This requires making an API call, so it should be robust
        # against transient errors.
        bot_username = call_reddit_with_retries(
            (lambda: reddit.user.me().name))
        _log_config_fn(log_to_console, log_to_file, log_dir, bot_username)
        # TODO maybe don't need to make a Reddit call here, since the user passes
        # their username for authentication purposes. Also, should print stuff
        # to console before configuring logs with bot name etc.
        log_info("Retrieved bot username: %s", bot_username)
        runner = _bot_runner_factory_fn(
            reddit,
            ItemProcessor(
                ItemFilter(
                    bot_username,
                    BASE_USER_BLACKLIST,
                    BASE_SUBREDDIT_BLACKLIST),
                ItemDataProcessor(self)))
        runner.start_loop()

    @unimplemented
    def reply_to_mention(self, username, text):
        pass

    @unimplemented
    def reply_using_parent_of_mention(self, username, text):
        pass

    @unimplemented
    def process_mention(self, item):
        pass
