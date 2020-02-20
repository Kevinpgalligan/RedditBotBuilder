from rbb.praw import is_post, author_name, subreddit_name, has_subreddit, has_author, get_text, has_text
from rbb.interfaces import is_implemented
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

    def start_loop(self, _loop_condition=always_true):
        while _loop_condition():
            self.process_inbox()
            time.sleep(RUN_INTERVAL_SECONDS)

    def process_inbox(self):
        for item in self.inbox.unread(limit=LIMIT_ON_INBOX):
            # Mark it as read so that we don't get stuck processing
            # the same comment over and over due to a bug.
            self.inbox.mark_read([item])
            self.item_processor.process(item)

class ItemProcessor:

    def __init__(self, item_filter, item_data_processor):
        self.item_filter = item_filter
        self.item_data_processor = item_data_processor

    def process(self, item):
        if self.item_filter.should_process_data(item):
            self.item_data_processor.process(item)

class ItemFilter:
    
    def __init__(self, bot_username, user_blacklist, subreddit_blacklist):
        self.bot_tag = "u/" + bot_username
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
        # TODO protection against the user f*cking up their implementation?
        if isinstance(item, Comment) and is_implemented(self.bot.reply_using_parent_of_mention):
            # TODO protection against parent being deleted?
            parent = item.parent()
            item.reply(
                self.bot.reply_using_parent_of_mention(
                    author_name(parent),
                    get_text(parent)))
        if has_text(item) and is_implemented(self.bot.reply_to_mention):
            item.reply(self.bot.reply_to_mention(author_name(item), get_text(item)))
        if is_implemented(self.bot.process_mention):
            self.bot.process_mention(item)
