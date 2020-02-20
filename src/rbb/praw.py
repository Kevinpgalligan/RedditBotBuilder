"""Contains utility functions for dealing with the Python Reddit API Wrapper (PRAW)."""

from praw.models import Comment, Submission
import praw.exceptions
import time

MAX_ATTEMPTS = 3
COOLDOWN_SECONDS = 10

def normalise(name):
    """Normalises a name on Reddit.
    fuNNy -> funny
    MyName -> myname
    bestsubredditever -> bestsubredditever"""
    return name.lower()

def is_post(item):
    """Returns whether the given item is a Comment or Submission."""
    return isinstance(item, Comment) or isinstance(item, Submission)

def has_author(item):
    """Returns whether the given item has an author."""
    # TODO maybe want to check if it's a string or None, too.
    # same goes for has_subreddit.
    return hasattr(item, "author")

def has_subreddit(item):
    return hasattr(item, "subreddit")

def author_name(item):
    """Returns normalised author name of the given post.
    If the author name can't be retrieved (due to the account being
    deleted, for example), then returns the string "[deleted]".
    If 'item' doesn't have an author, then raises ValueError."""
    if not has_author(item):
        raise ValueError(
            "Item {} does not have an author.".format(str(item)))
    if item.author is None:
        return "[deleted]"
    return item.author.name

def subreddit_name(item):
    """Returns normalised name of the subreddit to which the item belongs.
    If 'item' is not located in a Subreddit, then raises ValueError."""
    if not has_subreddit(item):
        raise ValueError(
            "Item {} is not located in a Subreddit.".format(str(item)))
    return item.subreddit.display_name

def has_text(item):
    return any(hasattr(item, a) for a in ["body", "selftext"])

def get_text(item):
    if isinstance(item, Submission):
        return item.selftext
    elif isinstance(item, Comment):
        return item.body
    raise ValueError("Tried to get text of unsupported item {}".format(item))

def call_reddit_with_retries(fn, _sleep_fn=time.sleep):
    """Runs the provided function with retries in case of transient errors like
    API rate-limiting and network errors."""
    attempts = 1
    while True:
        try:
            return fn()
        except (praw.exceptions.APIException, praw.exceptions.WebSocketException) as e:
            if attempts >= MAX_ATTEMPTS or (isinstance(e, praw.exceptions.APIException) and e.error_type != "RATELIMIT"):
                raise e
            _sleep_fn(COOLDOWN_SECONDS)
        attempts += 1
