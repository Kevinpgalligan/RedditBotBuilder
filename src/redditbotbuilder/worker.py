"""
Contains parts of bot functionality that are meant to run
indefinitely in a dedicated process.
"""

import time
from multiprocessing import Process
import abc

def always_true():
    return True

def do_forever(fn, _loop_condition_fn=always_true):
    while _loop_condition_fn():
        fn()

class Worker(abc.ABC):

    def __init__(self):
        self.process = Process(target=self.loop)

    def start(self):
        self.process.start()

    def stop(self):
        self.process.terminate()

    def loop(self):
        self.initialize_within_process()
        do_forever(self.do_work)

    @abc.abstractmethod
    def initialize_within_process(self):
        pass

    @abc.abstractmethod
    def do_work(self):
        pass

class RedditOwningWorker(Worker, abc.ABC):

    def __init__(self, reddit_factory):
        super(RedditOwningWorker, self).__init__()
        self.reddit_factory = reddit_factory

    def initialize_within_process(self):
        # Reddit instance must be created only once the
        # new process has started, otherwise it will be
        # pickled and passed from the first process, which
        # might corrupt it somehow.
        self.reddit = self.reddit_factory.create()

    @abc.abstractmethod
    def do_work(self):
        pass

class StreamWorker(Worker):

    def __init__(self, item_streamer_factory, ingestion_queue):
        super(StreamWorker, self).__init__()
        self.item_streamer_factory = item_streamer_factory
        self.ingestion_queue = ingestion_queue

    def initialize_within_process(self):
        # This contains a Reddit instance, which should be
        # created within the process rather than being pickled
        # and then passed to the process.
        self.item_streamer = self.item_streamer_factory.create()

    def do_work(self):
        items = self.item_streamer.get_next_batch()
        for item in items:
            self.ingestion_queue.put(item)
        time.sleep(4)

class FilterWorker(RedditOwningWorker):

    def __init__(self, reddit_factory, aggregate_ignore_conditions, ingestion_queue, processing_queue):
        super(FilterWorker, self).__init__(reddit_factory)
        self.aggregate_ignore_conditions = aggregate_ignore_conditions
        self.ingestion_queue = ingestion_queue
        self.processing_queue = processing_queue

    def do_work(self):
        # fix tuple hack?
        item, = self.ingestion_queue.get(self.reddit)
        action_ids = []
        cached_filter_results = {}
        for aggregate_ignore_condition in self.aggregate_ignore_conditions:
            if aggregate_ignore_condition.should_ignore(item, cached_filter_results):
                action_ids.append(aggregate_ignore_condition.action_id)
        if action_ids:
            self.processing_queue.put(item, action_ids)

class ProcessingWorker(RedditOwningWorker):

    def __init__(self, reddit_factory, actions, processing_queue):
        super(ProcessingWorker, self).__init__(reddit_factory)
        self.actions = actions
        self.processing_queue = processing_queue

    def do_work(self):
        item, action_ids = self.processing_queue.get(self.reddit)
        actions_to_execute = [action for action in self.actions if action.id in action_ids]
        for action in actions_to_execute:
            try:
                action.execute(item)
            except Exception as e:
                # Never stop processing.
                # todo print stack trace.
                print(e)