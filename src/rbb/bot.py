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

class RedditBot:
    def run(self):
        runner = BotRunner(auth.reddit_from_program_args(), self)
        runner.start_loop()

    def reply_to_mention(self, username, text):
        pass

    def reply_to_parent_of_mention(self, username, text):
        pass

    def process_mention(self, comment):
        pass

def normalise(name):
    return name.lower()

class BotRunner:
    
    filters = [
        is_post,
        self.is_tagged_in,
        self.interacted_too_many_times_in_thread,
        self.author_is_blacklisted,
        self.subreddit_is_blacklisted
    ]

    def __init__(self, reddit, bot):
        self.reddit = reddit
        self.bot = bot
        self.inbox = reddit.inbox
        self.user = normalise(reddit.user.me().name)
        self.post_counter_by_submission = defaultdict(int)

    def start_loop(self):
        while True:
            self.process_inbox()
            time.sleep(RUN_INTERVAL_SECONDS)

    def process_inbox(self):
        for item in self.inbox.unread(limit=LIMIT_ON_INBOX):
            # Mark it as read so that we don't get stuck processing
            # the same comment over and over due to a bug.
            self.inbox.mark_read([item])
            if self.passes_filters(item):
                pass # TODO stuff
                # TODO increment post counter

    def passes_filters(self, item):
        return all(f(item) for f in self.filters)

    def is_tagged_in(self, item):
        return self.user in item.body.lower()
    
    def interacted_too_many_times_in_thread(self, item):
        return self.post_counter_by_submission[item.link_id] > POST_LIMIT_PER_SUBMISSION

    def author_is_blacklisted(self, item):
        pass # TODO

    def subreddit_is_blacklisted(self, item):
        pass # TODO

def is_post(item):
    return isinstance(item, Comment) or isinstance(item, Submission)
