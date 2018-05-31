"""Utilities for working with the PRAW API.
"""

import praw
import sys

READ_CREDENTIAL_NAMES = ["client_id", "client_secret", "user_agent"]
WRITE_CREDENTIAL_NAMES = READ_CREDENTIAL_NAMES + ["username", "password"]
SETS_OF_CREDENTIAL_NAMES = [READ_CREDENTIAL_NAMES, WRITE_CREDENTIAL_NAMES]

class RedditFactory:

    def __init__(self, reddit_credentials):
        self.reddit_credentials = reddit_credentials

    def create(self):
        return self.reddit_credentials.instantiate_reddit()

class RedditCredentials:

    def __init__(self, credentials_dict, is_read_only):
        self.credentials_dict = credentials_dict
        self.is_read_only = is_read_only

    def instantiate_reddit(self, *args, **kwargs):
        return praw.Reddit(*args, **self.credentials_dict, **kwargs)

def normalized(s):
    return s.lower()

def normalized_author_name(item):
    return "[deleted]" if item.author is None else normalized(item.author.name)

def reddit_credentials_from_program_args(_args=sys.argv):
    """Creates a PRAW Reddit instance by reading credentials from sys.argv.

    The program is expected to be called like...

        `python program.py client_id client_secret user_agent`

    ...for a read-only Reddit instance, or like...

        `python program.py client_id client_secret user_agent username password`

    ...for a Reddit instance with read AND write permissions.

    See the PRAW docs for information on the meaning of these parameters:
        https://praw.readthedocs.io/en/latest/getting_started/quick_start.html

    :raises ValueError: if incorrect number of args were passed.
    :raises: any other error that may be raised by the PRAW Reddit constructor.
    :returns: a PRAW Reddit instance.
    """
    # todo fix this
    return RedditCredentials(dict(zip(WRITE_CREDENTIAL_NAMES, _args[1:])), True)

