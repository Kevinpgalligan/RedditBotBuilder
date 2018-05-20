from redditbotbuilder.util.praw import normalized_author_name

import abc

class Filterer:

    def __init__(self, ignore_condition_groups, ingestion_queue, processing_queue):
        self.ignore_condition_groups = ignore_condition_groups
        self.ingestion_queue = ingestion_queue
        self.processing_queue = processing_queue

    def run(self):
        while True:
            print("filterer is getting")
            item = self.ingestion_queue.get()
            print("got me an item!")
            ids_of_actions_that_should_process = []
            cached_filter_results = {}
            for ignore_condition_group in self.ignore_condition_groups:
                if ignore_condition_group.evaluate(item, cached_filter_results):
                    ids_of_actions_that_should_process.append(ignore_condition_group.action_id)
            print("actions to execute", ids_of_actions_that_should_process)
            if ids_of_actions_that_should_process:
                print("puttin' it on the queue!")
                self.processing_queue.put(
                    (item,
                    ids_of_actions_that_should_process))

# todo add note about how implementing classes should implement eq and hash
# todo check which conditions work for which types of item
class IgnoreCondition(abc.ABC):

    @abc.abstractmethod
    def should_ignore(self, item):
        return True

class IgnoreConditionGroup:

    def __init__(self, conditions, action_id):
        self.conditions = conditions
        self.action_id = action_id

    def evaluate(self, item, cached_filter_results):
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

