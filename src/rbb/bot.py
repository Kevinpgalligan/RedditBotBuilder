from rbb.praw import (is_post, author_name, subreddit_name, has_subreddit, has_author,
    get_text, has_text, normalise)
from rbb.interfaces import is_implemented
from rbb.logging import log_info, log_error
from praw.models import Comment, Submission
import time

# The API limits you to pulling 100 comments at a time, anyway.
LIMIT_ON_INBOX = 100
# Run once per minute.
RUN_INTERVAL_SECONDS = 60
# Prevents bot from getting stuck in infinite loops.
POST_LIMIT_PER_SUBMISSION = 5

def always_true():
    return True

# TODO add more item types; review other TODOs before doing so, as other
# types are not supported in some places.
SUPPORTED_ITEM_TYPES = [Comment, Submission]

def is_supported_item_type(item):
    return any(isinstance(item, cls) for cls in SUPPORTED_ITEM_TYPES)

class BotRunner:

    def __init__(self, reddit, item_processor):
        self.reddit = reddit
        self.inbox = reddit.inbox
        self.item_processor = item_processor

    def start_loop(self, _loop_condition=always_true, _sleep_fn=time.sleep):
        while _loop_condition():
            try:
                self.process_inbox()
            except Exception as e:
                # Don't crash the bot, even though it's possibly
                # a bug in the framework.
                log_error("Got exception, inbox processing interrupted: %s", e)
            _sleep_fn(RUN_INTERVAL_SECONDS)

    def process_inbox(self):
        for item in self.inbox.unread(limit=LIMIT_ON_INBOX):
            log_info("Got item from inbox: %s", str(item.__dict__))
            # Mark it as read so that we don't get stuck processing
            # the same item over and over due to a bug.
            self.inbox.mark_read([item])
            log_info("Marked item as read.")
            self.item_processor.process(item)
            log_info("Finished processing item.")

class ItemProcessor:

    def __init__(self, item_filter, item_data_processor):
        self.item_filter = item_filter
        self.item_data_processor = item_data_processor

    def process(self, item):
        if self.item_filter.should_process_data(item):
            self.item_data_processor.process(item)

class ItemFilter:
    
    def __init__(self, bot_username, user_blacklist, subreddit_blacklist):
        self.bot_tag = "u/" + normalise(bot_username)
        self.user_blacklist = user_blacklist
        self.subreddit_blacklist = subreddit_blacklist
        self.filters = [
            is_supported_item_type,
            self.is_tagged_in,
            self.author_is_blacklisted,
            self.subreddit_is_blacklisted
        ]

    def should_process_data(self, item):
        return all(f(item) for f in self.filters)

    def is_tagged_in(self, item):
        # TODO should return True for messages & possibly other item types. But
        # those aren't supported yet, so not a huge deal.
        return self.bot_tag in get_text(item).lower()

    def author_is_blacklisted(self, item):
        return not has_author(item) or author_name(item) not in self.user_blacklist

    def subreddit_is_blacklisted(self, item):
        return not has_subreddit(item) or subreddit_name(item) not in self.subreddit_blacklist

class ItemDataProcessor:

    def __init__(self, bot):
        self.bot = bot

    def process(self, item):
        # TODO abstract these, pairs of 1) condition / filter, and 2) the action.
        if isinstance(item, Comment) and is_implemented(self.bot.reply_using_parent_of_mention):
            parent = item.parent()
            item.reply(
                self.bot.reply_using_parent_of_mention(
                    author_name(parent),
                    get_text(parent)))
        if has_text(item) and is_implemented(self.bot.reply_to_mention):
            item.reply(self.bot.reply_to_mention(author_name(item), get_text(item)))
        if is_implemented(self.bot.process_mention):
            self.bot.process_mention(item)
