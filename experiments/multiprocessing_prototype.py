from redditbotbuilder.stream import CommentFetcher, CommentStreamer
from redditbotbuilder.filter import IgnoreConditionGroup, IsSelfIgnoreCondition, Filterer
from redditbotbuilder.process import ItemProcessor
from redditbotbuilder.action import CommentProcessingAction

import redditbotbuilder.util.praw

from multiprocessing import Queue
from multiprocessing import Process

def print_comment(comment):
    print(comment.body)

def main():
    reddit = redditbotbuilder.util.praw.create_reddit_from_program_args()
    subreddits = "testingground4bots"

    ingestion_queue = Queue()
    comment_fetcher = CommentFetcher(reddit, subreddits, 100)
    comment_streamer = CommentStreamer(comment_fetcher, ingestion_queue)
    Process(target=comment_streamer.run).start()

    action_id = "MyAction"

    processing_queue = Queue()
    ignore_condition_group = IgnoreConditionGroup(
        [IsSelfIgnoreCondition("herp")],
        action_id)
    filterer = Filterer([ignore_condition_group], ingestion_queue, processing_queue)
    Process(target=filterer.run).start()

    action = CommentProcessingAction(action_id, print_comment)
    item_processor = ItemProcessor([action], processing_queue)
    Process(target=item_processor.run).start()

if __name__ == "__main__":
    main()
