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
            _reddit_factory_fn=rbb.auth.get_reddit_from_program_args,
            _reddit_username_fn=rbb.auth.get_reddit_username_from_program_args,
            _bot_runner_factory_fn=BotRunner,
            _configure_logging_fn=rbb.logging.configure):
        reddit = _reddit_factory_fn()
        bot_username = _reddit_username_fn()
        _configure_logging_fn(log_to_console, log_to_file, log_dir, bot_username)
        log_info("Starting bot: u/%s", bot_username)
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
