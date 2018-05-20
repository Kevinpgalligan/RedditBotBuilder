"""Utilities for caching PRAW items so that they're not processed twice.
"""

import collections

class ItemCache:

    def __init__(self, size):
        self._cached_ids_queue = collections.deque(maxlen=size)
        self._cached_ids_set = set()

    def __contains__(self, item):
        """Returns whether the the cache contains this item.

        The item will not be added to the cache.

        :param item: a PRAW item, like a Comment or Submission.
        :return: True/False
        """
        return item.name in self._cached_ids_set

    def __len__(self):
        return len(self._cached_ids_set)

    def add_all(self, items):
        """Add a batch of items to the cache.

        Only the items' globally unique IDs (e.g. t5_6f6fh2) will be stored.

        The items that have been in the cache for longest will be overwritten
        once the cache reaches its size limit.

        :param items: an iterable of PRAW items.
        :returns: None"""
        if items:
            self._cached_ids_queue.extend(item.name for item in items)
            self._cached_ids_set = set(self._cached_ids_queue)
