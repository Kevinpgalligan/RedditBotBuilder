import rbb.auth
from rbb.auth import AuthorisationMethod
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
            auth_method=AuthorisationMethod.PROGRAM_ARGS,
            _get_auth_provider_fn=rbb.auth.get_auth_provider,
            _bot_runner_factory_fn=BotRunner,
            _configure_logging_fn=rbb.logging.configure):
        auth_provider = _get_auth_provider_fn(auth_method)
        reddit = auth_provider.get_reddit()
        bot_username = auth_provider.get_username()
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
