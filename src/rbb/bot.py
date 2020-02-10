# TODO
# - basic functionality (process mentions w/ user-defined functions).
# - think through possible loop-breaking errors (e.g. can't get bot's
#   own name due to rate-limiting).
# - actually test it.
# - unit tests.
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

import auth
import time
from collections import defaultdict
from praw import Comment, Submission

# The API limits you to pulling 100 comments at a time, anyway.
LIMIT_ON_INBOX = 100
# Run once per minute.
RUN_INTERVAL_SECONDS = 60
# Prevents bot from getting stuck in infinite loops.
POST_LIMIT_PER_SUBMISSION = 5

def normalise(name):
    return name.lower()

def normalised_set(*names):
    return set(map(normalise, names))

BASE_USER_BLACKLIST = normalised_set(
    "AutoModerator",
    # Don't know if this bot is still active, but it annoyed the
    # hell out of me by stalking AnEmojipastaBot.
    "Sub_Corrector_Bot"
)

BASE_SUBREDDIT_BLACKLIST = normalised_set(
    # There will always be sh*tbags who try to f*ck with people
    # in these subreddits.
    "SuicideWatch",
    "depression"
)

class RedditBot:
    def run(self, _bot_runner_factory_fn=BotRunner):
        runner = _bot_runner_factory_fn(
            auth.reddit_from_program_args(),
            self,
            BASE_USER_BLACKLIST,
            BASE_SUBREDDIT_BLACKLIST)
        runner.start_loop()

    def reply_to_mention(self, username, text):
        pass

    def reply_to_parent_of_mention(self, username, text):
        pass

    def process_mention(self, comment):
        pass

class BotRunner:

    filters = [
        is_post,
        self.is_tagged_in,
        self.interacted_too_many_times_in_thread,
        self.author_is_blacklisted,
        self.subreddit_is_blacklisted
    ]

    def __init__(self, reddit, bot, user_blacklist, subreddit_blacklist):
        self.reddit = reddit
        self.bot = bot
        self.inbox = reddit.inbox
        self.user = normalise(reddit.user.me().name)
        self.post_counter_by_submission = defaultdict(int)
        self.user_blacklist = user_blacklist
        self.subreddit_blacklist = subreddit_blacklist

    def start_loop(self, _loop_condition=always_true):
        while _loop_condition():
            self.process_inbox()
            time.sleep(RUN_INTERVAL_SECONDS)

    def process_inbox(self):
        for item in self.inbox.unread(limit=LIMIT_ON_INBOX):
            # Mark it as read so that we don't get stuck processing
            # the same comment over and over due to a bug.
            self.inbox.mark_read([item])
            if self.passes_filters(item):
                self.pass_to_bot(item)
                # TODO increment post counter

    def passes_filters(self, item):
        return all(f(item) for f in self.filters)

    def is_tagged_in(self, item):
        return self.user in item.body.lower()

    def interacted_too_many_times_in_thread(self, item):
        # TODO this is too restrictive...
        return self.post_counter_by_submission[item.link_id] > POST_LIMIT_PER_SUBMISSION

    def author_is_blacklisted(self, item):
        return author_name(item) in self.user_blacklist

    def subreddit_is_blacklisted(self, item):
        return subreddit_name(item) in self.subreddit_blacklist

    def pass_to_bot(self, item):
        # TODO call all of the bot's user-defined functions.
        pass

def always_true():
    return True

def is_post(item):
    return isinstance(item, Comment) or isinstance(item, Submission)

def author_name(item):
    # TODO check if this works for other item types, e.g. posts, messages...
    return "[deleted]" if item.author is None else normalise(item.author)

def subreddit_name(item):
    # TODO make sure that this isn't called for messages 
    return normalise(item.subreddit.display_name)
