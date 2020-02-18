# TODO
# - basic functionality (process mentions w/ user-defined functions).
# - think through possible loop-breaking errors (e.g. can't get bot's
#   own name due to rate-limiting).
# - actually test it.
# - integration tests to make sure that everything is wired up correctly
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

import rbb.auth
from rbb.praw import is_post, author_name, subreddit_name, normalise, has_subreddit, has_author
from rbb.lists import BASE_USER_BLACKLIST, BASE_SUBREDDIT_BLACKLIST
from praw.models import Comment, Submission
import time
from collections import defaultdict

# The API limits you to pulling 100 comments at a time, anyway.
LIMIT_ON_INBOX = 100
# Run once per minute.
RUN_INTERVAL_SECONDS = 60
# Prevents bot from getting stuck in infinite loops.
POST_LIMIT_PER_SUBMISSION = 5

def always_true():
    return True

def create_bot_runner(*args):
    return BotRunner(*args)

# TODO add more item types; review other TODOs before doing so, as other
# types are not supported in some places.
SUPPORTED_ITEM_TYPES = [Comment, Submission]

def is_supported_item_type(item):
    return any(isinstance(item, cls) for cls in SUPPORTED_ITEM_TYPES)

class RedditBot:

    def run(
            self,
            _reddit_factory_fn=rbb.auth.reddit_from_program_args,
            _bot_runner_factory_fn=create_bot_runner):
        # TODO this makes a call to Reddit, which might fail 
        reddit = _reddit_factory_fn()
        bot_username = normalise(reddit.user.me().name)
        runner = _bot_runner_factory_fn(
            reddit,
            ItemProcessor(
                ItemFilter(
                    bot_username,
                    BASE_USER_BLACKLIST,
                    BASE_SUBREDDIT_BLACKLIST),
                ItemDataProcessor(self)))
        runner.start_loop()

    def reply_to_mention(self, username, text):
        pass

    def reply_to_parent_of_mention(self, username, text):
        pass

    def process_mention(self, comment):
        pass

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
        return self.bot_username in item.body.lower()

    def author_is_blacklisted(self, item):
        return not has_author(item) or author_name(item) not in self.user_blacklist

    def subreddit_is_blacklisted(self, item):
        return not has_subreddit(item) or subreddit_name(item) not in self.subreddit_blacklist

class ItemDataProcessor:

    def __init__(self, bot):
        self.bot = bot

    def process(self, item):
        # TODO make calls to bot.
        # it'll be necessary for this class to have access to the Reddit instance.
        pass 
