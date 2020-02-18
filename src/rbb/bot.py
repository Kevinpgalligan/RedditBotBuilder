# TODO
# - actually test it.
# - think through possible loop-breaking errors (e.g. can't get bot's
#   own name due to rate-limiting).
# - think through extension of interface, e.g. adding more data that can
#   be passed cleanly to the bot. As of now, can't add new data without
#   breaking old interface. So should probably pass only a Data object
#   or Input object for each method, which can be expanded with new
#   attributes. Also, think really hard about the names, since they can't
#   be changed later.
# - manual tests: all scenarios where something gets deleted. reply to comment
#   of bot without mentioning it, just the name of the bot, see what happens.
# - see what methods on the models require a call to the API, make sure that
#   they are not being used if unnecessary (eg user hasn't implemented method
#   that requires them).
# - integration tests to make sure that everything is wired up correctly,
#   and improve RedditBot tests.
# - limit number of interactions (by user, by thread, etc). And allow
#   this to be customised.
# - whitelisting.
# - set up logging (customisable).
# - specify location to save state (logs, blacklist, post count, etc).
# - different methods of providing credentials.
# - updateable blacklisting / whitelisting.
# - footers.
# - saving state (+ read previous state on start-up).
# - go through all inline TODOs and fix them.
# - (STRETCH GOAL) receive commands.
# - (STRETCH GOAL) alarming, health status

# thoughts on commands....
# allow specification of "owner".
# owner can run other commands:
#     pause
#     stop
#     send stats
#     send state?
# make it flexible enough that users can send commands through comments, too?
# the command thing is interesting... different privilege levels.
# it can only be blacklisted from a subreddit by a moderator of that subreddit.
# owner can blacklist users, subreddits, whatever. And whitelist subreddits.
# multiple owners?

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
        self.bot_username = bot_username
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
        # TODO make this more robust? Should there be a u/ before the username,
        # or is that included in 'user' anyway? Shouldn't work if the "tag" is
        # actually a substring of a bigger word.
        # TODO should return True for messages & possibly other item types. But
        # those aren't supported yet, so not a huge deal.
        return self.bot_username in get_text(item).lower()

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
