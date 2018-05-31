from redditbotbuilder.util.queue import RedditItemQueue
from redditbotbuilder.worker import (
    StreamWorker,
    FilterWorker,
    ProcessingWorker)
from redditbotbuilder.stream import ItemStreamerFactory
from redditbotbuilder.util.praw import RedditFactory

class Pipeline:

    def __init__(self, item_fetcher_constructor, limit, aggregate_ignore_conditions, actions):
        self.item_fetcher_constructor = item_fetcher_constructor
        self.limit = limit
        self.aggregate_ignore_conditions = aggregate_ignore_conditions
        self.actions = actions

class RedditBot:

    def __init__(self, reddit_credentials, pipelines):
        self.reddit_credentials = reddit_credentials
        self.pipelines = pipelines
        self.workers = []

    def run(self):
        for pipeline in self.pipelines:
            self._instantiate_pipeline_workers(pipeline)
        self._instantiate_resource_allocation_worker()
        self._start_workers()
        # todo wait for end, monitor worker health, kill workers on end.

    def _instantiate_pipeline_workers(self, pipeline):
        ingestion_queue = RedditItemQueue()
        processing_queue = RedditItemQueue()

        reddit_factory = RedditFactory(self.reddit_credentials)

        self.workers.extend([
            StreamWorker(
                ItemStreamerFactory(
                    pipeline.item_fetcher_constructor,
                    reddit_factory,
                    pipeline.limit),
                ingestion_queue),
            FilterWorker(
                reddit_factory,
                pipeline.aggregate_ignore_conditions,
                ingestion_queue,
                processing_queue),
            ProcessingWorker(
                reddit_factory,
                pipeline.actions,
                processing_queue)
        ])

    def _instantiate_resource_allocation_worker(self):
        pass #todo

    def _start_workers(self):
        for worker in self.workers:
            worker.start()
