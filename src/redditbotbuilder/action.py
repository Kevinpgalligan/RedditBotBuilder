import praw.exceptions

import abc
import time

class ActionExecutionException(Exception):

    def __init__(self, msg, cause):
        super(msg, cause)

class Action(abc.ABC):

    SECONDS_TO_WAIT_AFTER_RATE_LIMITING = 600

    def __init__(self, id, _sleep_fn=time.sleep):
        self.id = id
        self._sleep_fn = _sleep_fn

    def execute(self, item):
        """Do a unit of work on the provided Reddit item.

        :raises ActionExecutionException: if non-rate-limiting exception is raised during execution.
        :returns: None
        """
        try:
            self.do_execute(item)
        except praw.exceptions.APIException as e:
            if e.error_type == "RATELIMIT":
                # Wait for rate-limiting to pass, then try again.
                self._sleep_fn(Action.SECONDS_TO_WAIT_AFTER_RATE_LIMITING)
                self.execute(item)
        except Exception as e:
            raise ActionExecutionException(
                "Encountered exception during execution of {}.".format(self.__class__),
                e)

    @abc.abstractmethod
    def do_execute(self, item):
        return

class CommentProcessingAction(Action):

    def __init__(self, id, comment_processing_fn):
        super(CommentProcessingAction, self).__init__(id)
        self.comment_processing_fn = comment_processing_fn

    def do_execute(self, comment):
        self.comment_processing_fn(comment)
