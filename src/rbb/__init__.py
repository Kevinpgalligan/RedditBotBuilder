import rbb.auth
from rbb.praw import normalise
from rbb.bot import BotRunner, ItemProcessor, ItemFilter, ItemDataProcessor
from rbb.lists import BASE_USER_BLACKLIST, BASE_SUBREDDIT_BLACKLIST
from rbb.interfaces import unimplemented

class RedditBot:

    def run(
            self,
            _reddit_factory_fn=rbb.auth.reddit_from_program_args,
            _bot_runner_factory_fn=BotRunner):
        # TODO this makes a call to Reddit, which might fail 
        reddit = _reddit_factory_fn()
        bot_username = normalise(reddit.user.me().name)
        runner = _bot_runner_factory_fn(
            reddit,
            ItemProcessor(
                ItemFilter(
                    bot_username,
                    BASE_USER_BLACKLIST,
                    BASE_SUBREDDIT_BLACKLIST),
                ItemDataProcessor(self)))
        runner.start_loop()

    @unimplemented
    def reply_to_mention(self, username, text):
        pass

    @unimplemented
    def reply_using_parent_of_mention(self, username, text):
        pass

    @unimplemented
    def process_mention(self, item):
        pass
