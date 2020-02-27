import rbb.auth
from rbb.auth import AuthorisationMethod
from rbb.praw import normalise, call_reddit_with_retries, has_text, author_name, get_text
from rbb.bot import BotRunner, ItemProcessor, ItemFilter, ItemDataProcessor
from rbb.lists import BASE_USER_BLACKLIST, BASE_SUBREDDIT_BLACKLIST
from rbb.interfaces import unimplemented, is_implemented
import rbb.logging
from rbb.logging import log_info
from abc import ABC, abstractmethod
from praw.models import Comment, Submission

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
        bot_callers = [
            ParentReplyBotCaller(),
            ReplyBotCaller(),
            ProcessItemBotCaller()
        ]
        log_info(
            "With the following bot actions: %s",
            ", ".join("'" + caller.description() + "'" for caller in bot_callers))
        runner = _bot_runner_factory_fn(
            reddit,
            ItemProcessor(
                ItemFilter(
                    bot_username,
                    BASE_USER_BLACKLIST,
                    BASE_SUBREDDIT_BLACKLIST),
                ItemDataProcessor(
                    self,
                    bot_callers)))
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

class BotCaller(ABC):
    """These classes define when and how to pass data from a Reddit item to the bot. Might seem like overkill, but it's much easier to test this way."""

    @abstractmethod
    def should_call(self, bot, item):
        """Returns (should_call,reason), where 'should_call' is a boolean and 'reason' is a string explanation of why it should or should not call the bot."""
        pass

    @abstractmethod
    def call(self, bot, item):
        """Doesn't return anything, just calls the bot."""
        pass

    @abstractmethod
    def description(self):
        """Returns a string describing the type of action that this caller invokes in the bot."""
        pass

class ParentReplyBotCaller(BotCaller):

    def should_call(self, bot, item):
        if not isinstance(item, Comment):
            return False, "item is not a comment and hence doesn't have a parent"
        if not is_implemented(bot.reply_using_parent_of_mention):
            return False, "bot does not have implementation of corresponding method"
        return True, None

    def call(self, bot, item):
        parent = item.parent()
        item.reply(
            bot.reply_using_parent_of_mention(
                author_name(parent),
                get_text(parent)))

    def description(self):
        return "reply to comment using data from its parent"

class ReplyBotCaller(BotCaller):
    
    def should_call(self, bot, item):
        if not has_text(item):
            return False, "item does not have a text field, there's nothing to reply to"
        if not is_implemented(bot.reply_to_mention):
            return False, "bot does not have implementation of corresponding method"
        return True, None

    def call(self, bot, item):
        item.reply(bot.reply_to_mention(author_name(item), get_text(item)))

    def description(self):
        return "reply to a Reddit item that has text data"

class ProcessItemBotCaller(BotCaller):
    
    def should_call(self, bot, item):
        if not is_implemented(bot.process_mention):
            return False, "bot does not have implementation of corresponding method"
        return True, None

    def call(self, bot, item):
        bot.process_mention(item)

    def description(self):
        return "process any item"
