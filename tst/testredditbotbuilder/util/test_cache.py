from unittest.mock import Mock

from redditbotbuilder.util.cache import ItemCache

def mock_item(identifier):
    mock_item = Mock()
    mock_item.name = identifier
    return mock_item

SOME_ID = "blah"
ANOTHER_ID = "foo"
AND_ANOTHER_ID = "bar"

SIZE = 2

class TestItemCache:

    def setup_method(self):
        self.cache = ItemCache(SIZE)

    def test_contains_when_cache_is_empty(self):
        assert mock_item(SOME_ID) not in self.cache

    def test_contains_when_item_is_in_cache(self):
        item = mock_item(SOME_ID)
        self.cache.add_all([item])
        assert item in self.cache

    def test_contains_when_some_items_in_cache_but_queried_one_is_not(self):
        item = mock_item(SOME_ID)
        self.cache.add_all([mock_item(ANOTHER_ID), mock_item(AND_ANOTHER_ID)])
        assert item not in self.cache

    def test_add_all_when_item_gets_pushed_out(self):
        first = mock_item(SOME_ID)
        rest = [mock_item(an_id) for an_id in [ANOTHER_ID, AND_ANOTHER_ID]]

        self.cache.add_all([first])
        self.cache.add_all(rest)

        assert first not in self.cache
        for item in rest:
            assert item in self.cache
        assert 2 == len(self.cache)

    def test_add_all_no_items_in_batch(self):
        self.cache.add_all([])

    def test_add_all_when_trying_to_add_more_than_size_allows(self):
        items = [mock_item(an_id) for an_id in [SOME_ID, ANOTHER_ID, AND_ANOTHER_ID]]
        self.cache.add_all(items)

        assert items[0] not in self.cache
        for item in items[1:]:
            assert item in self.cache

    def test_add_duplicate_item(self):
        self.cache.add_all([mock_item(SOME_ID), mock_item(SOME_ID)])
        assert 1 == len(self.cache)
        assert mock_item(SOME_ID) in self.cache

    def test_len_when_empty(self):
        assert 0 == len(self.cache)

    def test_len_when_not_empty(self):
        self.cache.add_all([mock_item(SOME_ID)])
        assert 1 == len(self.cache)

