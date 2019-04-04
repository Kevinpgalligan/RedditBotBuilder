## Description
This is the prototype of a framework for developing Reddit bots. Its aim is to reduce the amount of code needed to develop robust bots using PRAW (Python Reddit API Wrapper). Here's what the API looks like:

```python
import redditbotbuilder

redditbotbuilder.of_program_args()\
    .with_comment_processing(lambda comment: print(comment.body))\
    .build()\
    .run()
```

This bot reads incoming comments from r/all and prints them. It can be started
from the command line with the following command:

```
python ./my-bot.py <client_id> <client_secret> <user_agent> <username> <password>
```

The framework handles the code that is common to most bots: passing credentials to their script and to PRAW's Reddit constructor, streaming content from Reddit, avoiding infinite loops with other bots, blacklisting certain subreddits / users, handling exceptions from the Reddit API, and so on.

Several actions can be attached to the same bot:

```python
import redditbotbuilder

def do_cool_thing_with_submission(submission):
    # do cool thing here
    pass

redditbotbuilder.of_program_args(subreddits=["mysubreddit", "mysubreddit2"])\
    .with_comment_processing(lambda comment: print(comment.body))\
    .with_submission_processing(do_cool_thing_with_submission)\
    .with_username_tag_processing(lambda comment: comment.reply("hello!"))\
    .build()\
    .run()
```

Under the hood, the framework creates multiple streams of "items" from Reddit: one for comments, one for submissions, one for private messages, etc. Each stream is handled by separate threads and executes the user-supplied functions on the items. The items can also be filtered, e.g. by author. Many other features have been imagined, such as convenience functions for attaching footers to the bot's replies; monitoring of the bot so that the owner is notified if it crashes; and built-in dynamic blacklisting (e.g. someone can PM the bot "blacklist me" and the bot will not reply to comments by that user). Users of the API can easily add these features to their bot, if they wish, through the bot builder.

However, due to the shortcomings of Python's / PRAW's concurrency support, the framework has been abandoned for now.
