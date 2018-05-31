from redditbotbuilder.util.cache import ItemCache

import time
import abc

class ItemStreamer:
    """Fetch new PRAW items from reddit and don't return the same one in successive calls.
    """

    def __init__(self, fetcher, fetch_limit, _cache_constructor=ItemCache, _time_fn=time.time):
        self.fetcher = fetcher
        self.fetch_limit = fetch_limit
        # Cache should be able to hold the number of items returned
        # by the Reddit API.
        self._cache = _cache_constructor(fetch_limit)
        self._start_timestamp = _time_fn()

    def get_next_batch(self):
        """Each call will return the next batch of new items.

        The same item will never be returned twice.

        :return: a list of new items. No guarantee is made about their order.
        """
        items = list(self.fetcher.fetch(self.fetch_limit))
        # Avoid allocating new memory here.
        start_index_of_old_items = _partition(items, self._is_old)
        del items[start_index_of_old_items:]
        self._cache.add_all(items)
        return items

    def _is_old(self, item):
        # Ensure that we don't process the same items again if the stream restarts
        # (e.g. due to script being stopped & started).
        return (item.created_utc < self._start_timestamp
                or item in self._cache)

def _partition(items, condition):
    # Sorts list (in-place) into 2 parts based on a condition. Items
    # for which the condition is False will be on the left; Trues will be on
    # the right.
    # Returns index of the start of the True part.
    items.sort(key=condition)
    return next((index for index, item in enumerate(items) if condition(item)), len(items))

class ItemFetcher(abc.ABC):

    @abc.abstractmethod
    def fetch(self, limit):
        return

class ItemStreamerFactory:

    def __init__(self, fetcher_constructor, reddit_factory, limit, *fetcher_args, **fetcher_kwargs):
        self.fetcher_constructor = fetcher_constructor
        self.reddit_factory = reddit_factory
        self.limit = limit
        self.fetcher_args = fetcher_args
        self.fetcher_kwargs = fetcher_kwargs

    def create(self):
        return ItemStreamer(
            self.fetcher_constructor(
                self.reddit_factory.create(),
                *self.fetcher_args,
                **self.fetcher_kwargs),
            self.limit)

class CommentFetcher(ItemFetcher):

    def __init__(self, reddit, subreddits):
        self.reddit = reddit
        self.subreddits = subreddits

    def fetch(self, limit):
        return self.reddit.subreddit(self.subreddits)\
            .comments(limit=limit)
