from redditbotbuilder.stream import CommentFetcher
from redditbotbuilder.filter import (
    AggregateIgnoreCondition,
    IsSelfIgnoreCondition)
from redditbotbuilder.action import CommentProcessingAction
from redditbotbuilder.bot import (
    RedditBot,
    Pipeline)

import redditbotbuilder.util.praw

import cProfile

def print_comment(comment):
    pass

def fetcher_constructor(reddit, *args, **kwargs):
    return CommentFetcher(reddit, "all")

"""
def main():
    cProfile.run("do_main()", "bot-profiling")
"""

def main():
    action_id = "MyAction"
    bot = RedditBot(
        redditbotbuilder.util.praw.reddit_credentials_from_program_args(),
        [
            Pipeline(
                fetcher_constructor,
                100,
                [AggregateIgnoreCondition(
                    [IsSelfIgnoreCondition("herp")],
                    action_id)],
                [CommentProcessingAction(action_id, print_comment)])
        ]
    )
    bot.run()


if __name__ == "__main__":
    main()
