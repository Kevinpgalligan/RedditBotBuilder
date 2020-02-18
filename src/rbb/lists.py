from rbb.praw import normalise

class Blacklist:
    """Basically a set of strings, but makes sure that all elements are
    normalised (i.e. cast to lower-case)."""

    def __init__(self, *names):
        self.contents = {normalise(name) for name in names}

    def add(self, name):
        self.contents.add(normalise(name))

    def __contains__(self, name):
        return normalise(name) in self.contents

    def __add__(self, other):
        return Blacklist(*list(self.contents | other.contents))

    def __eq__(self, other):
        return isinstance(other, Blacklist) and self.contents == other.contents

BASE_USER_BLACKLIST = Blacklist(
    "AutoModerator",
    # Don't know if this bot is still active, but it annoyed the
    # hell out of me by stalking AnEmojipastaBot.
    "Sub_Corrector_Bot"
)

BASE_SUBREDDIT_BLACKLIST = Blacklist(
    # There will always be sh*tbags who try to f*ck with people
    # in these subreddits.
    "SuicideWatch",
    "depression"
)
