import abc

class ActionExecutionException(Exception):

    def __init__(self, msg, cause):
        super(msg, cause)

class Action(abc.ABC):

    """

    :raises ActionExecutionException: if any type of exception is thrown during execution of action.
    """
    def execute(self, *args, **kwargs):
        try:
            self.do_execute(*args, **kwargs)
        except Exception as e:
            # Catch all types of exceptions, we don't know what might be thrown by an
            # implementing class.
            # todo handle rate-limiting exception, here or elsewhere.
            raise ActionExecutionException("Exception while executing action.", e)

    @abc.abstractmethod
    def do_execute(self, *args, **kwargs):
        return

# TODO: this is baaaaaaaaaaaad.
def execute_actions_on(actions, *args, **kwargs):
    """Executes a list of actions on the provided args. If an action
    throws an exception, it is caught and logged; this will not affect
    the execution of the other actions.

    :param actions: a list of Action objects to be executed.
    """
    for action in actions:
        try:
            action.execute(*args, **kwargs)
        except ActionExecutionException as e:
            # todo add logging
            pass

class CommentProcessingAction(Action):

    def __init__(self, comment_processing_fn):
        self.comment_processing_fn = comment_processing_fn

    def do_execute(self, comment):
        self.comment_processing_fn(comment)
