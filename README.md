## Description
This project, to develop a Reddit bot framework, was born from my experience of making Reddit bots
through PRAW (Python Reddit API Wrapper). PRAW
is great, but it isn't tailored towards the creation of bots. There is common code that everyone
who wants to create a bot must write: passing credentials to their script and to PRAW's Reddit 
constructor, streaming content from Reddit, handling edge cases (e.g. infinite loop if another bot responds
to your bot, blacklisting certain subreddits / users, handling various exceptions from the Reddit API), and so on.
This gave me the idea of handling all the common code in a framework.

After experimenting for a month or two, I developed the skeleton of the project and a neat API.
Here's what the API, making heavy use of the Builder pattern, was originally supposed to look like:

```python
import redditbotbuilder

redditbotbuilder.of_program_args()\
    .with_comment_processing(lambda comment: print(comment.body))\
    .build()\
    .run()
```

A bot running this code could be started from the command line with the following command:

```
python ./my-bot.py <client_id> <client_secret> <user_agent> <username> <password>
```

The bot would then read all incoming comments from r/all and print them.

A few lines of code to create the bot, while abstracting away all of the details of how
the data is pulled from Reddit and handling most of the edge cases. It could take
100+ lines of code if a user were to write this bot from scratch using only the PRAW API.

Several actions could be attached to the same bot:

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

Under the hood, the framework would create multiple streams of "items" from Reddit: one for
comments, one for submissions, one for private messages, etc. Each stream would be handled by
one or more threads and would execute the user-supplied functions on the items. The user could
also pass a filter during the construction of the bot so that, for example, only messages from a
particular author would be processed. Many other features were imagined, such as convenience
functions for attaching footers to the bot's replies; monitoring of the bot so that the owner would
be notified if it crashed; built-in dynamic blacklisting (e.g. someone can PM the bot "blacklist me"
and the bot will not reply to comments by that user); etc. Users of the API could easily add these
features to their bot, if they wished, through the bot builder.

However, the project immediately ran into a hurdle: Python's lack of support for multithreading.
There is no way to have multiple threads running on a single Python interpreter at the same time.
If you have two threads, then only one of them can be in control at once. There is a hacky
workaround for this: the multiprocessing module. Instead of threads, this module creates multiple
processes, each with their own Python interpreter.
 
The use of multiple processes brought up more issues: all code calling the
multiprocessing module has to be wrapped in a main method, and it can't process lambdas, so the
redditbotbuilder API was going to be more bloated and less elegant than before. Also, since each
interpreter would have its own copy of PRAW's Reddit client, and each of those clients would have
separate rate-limit controls, there would have to be a separate process to "allocate" Reddit requests
to the other processes so that the bot wouldn't get throttled by Reddit for making too many requests (for
example, if there were 2 processes, PRAW would allow them both to make `LIMIT - 1` requests to Reddit per
minute. Together, they would exceed the rate limit imposed by the Reddit API, and the bot would get throttled).
Lots of complexity to deal with there.

Fast forward to now: I have produced a prototype without the request-allocation part, but there is a mysterious
bug where the PRAW client returns batches of 0 comments, followed by batches of 150 comments (the max
number of comments you can retrieve at once, so obviously there are some comments missing). And to be honest,
I am fed up with battling the multiprocessing module, PRAW (which does not support multiprocessing) and
the Reddit API. So here is where I officially call it quits.

It hasn't been totally unproductive, however. Some of the lessons I learned:
* Dive into the most ambiguous and challenging parts of a project first, as they might kill the
project at a later stage, wasting your earlier effort.
* Don't focus on code quality (unit tests, refactoring, optimization, etc) during the prototyping phase, since
you might have to throw away all of the code later. And it's not good for motivation.
* If concurrency is needed, look elsewhere than Python.

Overall, it has been a fun project, and I especially enjoyed dreaming up the API. Someone else is
free to carry on with my work or use the idea for their own project.
