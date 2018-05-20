"""Convenience utilities for working with the PRAW API.

This includes concise functions for instantiating Reddit instances.
"""

import praw
import sys

READ_CREDENTIAL_NAMES = ["client_id", "client_secret", "user_agent"]
WRITE_CREDENTIAL_NAMES = READ_CREDENTIAL_NAMES + ["username", "password"]
SETS_OF_CREDENTIAL_NAMES = [READ_CREDENTIAL_NAMES, WRITE_CREDENTIAL_NAMES]

def normalized(s):
    return s.lower()

def normalized_author_name(item):
    return "[deleted]" if item.author is None else normalized(item.author.name)

def create_reddit_from_program_args(_reddit_constructor=praw.Reddit, _args=sys.argv):
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
    return _reddit_constructor(**_get_parameters(_args))

def _get_parameters(args):
    credentials = args[1:]
    for names in SETS_OF_CREDENTIAL_NAMES:
        if len(credentials) == len(names):
            return dict(zip(names, credentials))
    raise _parse_args_value_error(credentials)

def _parse_args_value_error(credentials):
    lines = [
        "Got credentials of size {}: {}".format(len(credentials), repr(credentials)),
        "Expected one of the following:"
    ]
    for names in SETS_OF_CREDENTIAL_NAMES:
        lines.append("  " + repr(names))
    return ValueError("\n".join(lines))

