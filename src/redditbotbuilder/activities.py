import abc

from .actions import execute_actions_on

class Activity(abc.ABC):

    def run(self):
        return

class SubredditCommentScanningActivity(Activity):

    COMMENTS_PER_SCAN = 100

    def __init__(self, reddit, subreddits, comment_processing_actions, filter_fns):
        """
        :param reddit: PRAW reddit instance.
        :param subreddits: (string) subreddits to scan, e.g. 'all' or 'funny' or 'funny+botwatch'.
        :param comment_processing_actions: a list of CommentProcessingAction objects,
        these actions are executed on the comments.
        :param filter_fns: functions used to filter out comments. Should take a comment and return
        true or false, example. Example...
            def filter(comment):
                return "Hello" in comment.body
        """
        self._reddit = reddit
        self._subreddits = subreddits
        self._comment_processing_actions = comment_processing_actions
        self._filter_fns = filter_fns[:]
        self._filter_fns.append(self._is_newer_than_last_scanned_comment)
        self._timestamp_of_last_scanned_comment = 0

    def run(self):
        for comment in self._generate_comments():
            self._timestamp_of_last_scanned_comment = max(
                self._timestamp_of_last_scanned_comment,
                comment.created_utc)
            execute_actions_on(self._comment_processing_actions, comment)

    def _generate_comments(self):
        return filter(
            self._passes_all_filters,
            self._reddit.subreddit(self._subreddits)\
                .comments(limit=SubredditCommentScanningActivity.COMMENTS_PER_SCAN))

    def _passes_all_filters(self, comment):
        return all(filter_fn(comment) for filter_fn in self._filter_fns)

    # This filter should ensure that we don't process the same comment twice.
    def _is_newer_than_last_scanned_comment(self, comment):
        return comment.created_utc > self._timestamp_of_last_scanned_comment
