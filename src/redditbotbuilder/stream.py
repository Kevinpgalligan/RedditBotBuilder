from redditbotbuilder.util.cache import ItemCache

import time

DEFAULT_ITEM_LIMIT = 100

class CommentStreamer:

    def __init__(self, comment_fetcher, ingestion_queue):
        self.comment_fetcher = comment_fetcher
        self.ingestion_queue = ingestion_queue

    def run(self):
        while True:
            print("well here we are")
            comments = self.comment_fetcher.get_next_batch()
            for comment in comments:
                self.ingestion_queue.put(comment)
            time.sleep(4)

class CommentFetcher:

    def __init__(self, reddit, subreddits, limit):
        self.item_fetcher = ItemFetcher(
            reddit.subreddit(subreddits).comments,
            limit=limit)

    def get_next_batch(self):
        return self.item_fetcher.get_next_batch()

class ItemFetcher:
    """Fetch new PRAW items from reddit and don't return the same one in successive calls.
    """

    def __init__(self, fetch_fn, limit=DEFAULT_ITEM_LIMIT, _cache_constructor=ItemCache, _time_fn=time.time):
        """
        EXAMPLE
        If you want to get the 50 newest comments from each call:

            ItemStreamer(subreddit.comments, limit=50)

        :param fetch_fn: a PRAW callable that gets a batch of new items
            from Reddit. Must accept 'limit' as a keyword argument. It should
            return from the same source every time, as otherwise there will
            be no guarantee that the same items are never returned twice.
        :param limit: max number of items to return in a batch. This
            will be passed as a keyword arg to the stream function.
            Defaults to 100.
        """
        self._fetch_fn = fetch_fn
        self._limit = limit
        # Cache should be able to hold the number of items returned
        # by the fetching function (at least).
        self._cache = _cache_constructor(limit)
        self._start_timestamp = _time_fn()

    def get_next_batch(self):
        """Each call will return the next batch of new items.

        The same item will never be returned twice.

        :return: a list of new items. No guarantee is made about their order.
        """
        items = list(self._fetch_fn(limit=self._limit))
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
