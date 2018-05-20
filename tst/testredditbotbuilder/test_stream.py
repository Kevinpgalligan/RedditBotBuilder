from unittest.mock import Mock

from redditbotbuilder.stream import ItemFetcher

LIMIT = 100

def mock_item(cache_contains, timestamp):
    item = Mock()
    item.created_utc = timestamp
    # These are attributes used for testing, they wouldn't
    # be found as part of a real item.
    item.cache_contains = cache_contains
    item.name = str(cache_contains) + "-" + str(timestamp)
    return item

START_TIMESTAMP = 2
OLD_TIMESTAMP = START_TIMESTAMP - 1
YOUNG_TIMESTAMP = START_TIMESTAMP + 1

OLD_NOT_IN_CACHE = mock_item(False, OLD_TIMESTAMP)
OLD_IN_CACHE = mock_item(True, OLD_TIMESTAMP)
ON_BORDER_NOT_IN_CACHE = mock_item(False, START_TIMESTAMP)
ON_BORDER_IN_CACHE = mock_item(True, START_TIMESTAMP)
YOUNG_NOT_IN_CACHE = mock_item(False, YOUNG_TIMESTAMP)
YOUNG_IN_CACHE = mock_item(True, YOUNG_TIMESTAMP)

def validate_get_next_batch(expected_result, streamed_items):
    def cache_contains(item):
        return item.cache_contains
    cache = Mock()
    cache.__contains__ = Mock(side_effect=cache_contains)
    cache.add_all = Mock()
    stream_fn = Mock(return_value=streamed_items)
    cache_constructor = Mock(return_value=cache)
    time_fn = Mock(return_value=START_TIMESTAMP)
    fetcher = ItemFetcher(stream_fn, limit=LIMIT, _cache_constructor=cache_constructor, _time_fn=time_fn)

    result = fetcher.get_next_batch()

    cache_constructor.assert_called_once_with(LIMIT)
    stream_fn.assert_called_once_with(limit=LIMIT)
    assert expected_result == result
    cache.add_all.assert_called_once_with(expected_result)

class TestItemFetcher:

    def test_stream_fn_returns_empty(self):
        validate_get_next_batch([], [])

    def test_get_next_batch_old_item_not_in_cache(self):
        validate_get_next_batch([], [OLD_NOT_IN_CACHE])

    def test_get_next_batch_old_item_also_in_cache(self):
        validate_get_next_batch([], [OLD_IN_CACHE])

    def test_get_next_batch_item_with_start_timestamp_but_in_cache(self):
        validate_get_next_batch([], [ON_BORDER_IN_CACHE])

    def test_get_next_batch_item_with_start_timestamp_and_not_in_cache(self):
        validate_get_next_batch([ON_BORDER_NOT_IN_CACHE], [ON_BORDER_NOT_IN_CACHE])

    def test_get_next_batch_young_item_not_in_cache(self):
        validate_get_next_batch([YOUNG_NOT_IN_CACHE], [YOUNG_NOT_IN_CACHE])

    def test_get_next_batch_young_item_in_cache(self):
        validate_get_next_batch([], [YOUNG_IN_CACHE])

    def test_get_next_batch_when_mix_of_types(self):
        validate_get_next_batch(
            [YOUNG_NOT_IN_CACHE, ON_BORDER_NOT_IN_CACHE],
            [YOUNG_NOT_IN_CACHE, OLD_NOT_IN_CACHE, ON_BORDER_IN_CACHE, ON_BORDER_NOT_IN_CACHE, OLD_IN_CACHE, YOUNG_IN_CACHE])
