from redditbotbuilder.util.praw import normalized_author_name

import abc

# todo add note about how implementing classes should implement eq and hash
# todo check which conditions work for which types of item
class IgnoreCondition(abc.ABC):

    @abc.abstractmethod
    def should_ignore(self, item):
        return True

class AggregateIgnoreCondition:

    def __init__(self, conditions, action_id):
        self.conditions = conditions
        self.action_id = action_id

    def should_ignore(self, item, cached_filter_results):
        for condition in self.conditions:
            if condition not in cached_filter_results:
                cached_filter_results[condition] = condition.should_ignore(item)
            if cached_filter_results[condition]:
                return False
        return True

class IsSelfIgnoreCondition(IgnoreCondition):

    def __init__(self, bot_name):
        self.bot_name = bot_name

    def should_ignore(self, item):
        return normalized_author_name(item) == self.bot_name

    def __eq__(self, other):
        return (isinstance(other, self.__class__)
            and other.bot_name == self.bot_name)

    def __hash__(self):
        return hash(self.bot_name)

