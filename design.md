# MVP (TODO)
* ask why tags don't work in submissions.
* add stack trace to exception logging, if possible.
* (20 mins) add tests for BotCaller classes -- and refactor, if thought to be necessary.
* (30 mins) Refactor: make names nicer (ideas: "tag" instead of "mention". "InteractiveBot" and "ScannerBot" rather than "RedditBot"), and allow extension of interface, e.g. adding more data that can be passed cleanly to the bot. As of now, can't add new data without breaking old interface. So should probably pass only a Data object or Input object for each method, which can be expanded with new attributes.
* (10 mins) (non-critical) wrap calls to user-defined functions with retries.
* (5 mins) (quick check) see what methods on the models require a call to the API, make sure that they are not being used unnecessarily (eg user hasn't implemented method that requires them).
* (30 mins) manual tests: all scenarios where something gets deleted. reply to comment of bot without mentioning it, just the name of the bot, see what happens. And fix these edge cases.
* (1 hour) limit number of interactions (by user, by thread, etc). And allow this to be customised.
* (45 mins) whitelisting (+ add more to the blacklist on start-up).
* (30 mins) different methods of providing credentials.
* (1 hour) saving state (+ read previous state on start-up). Specify location to save state (logs, blacklist, post count, etc).

* (1 hour) Scanner bot, rather than a bot that just replies to mentions.
* go through all inline TODOs and fix them.
* (2 hours) All of the soft stuff. Documentation, PyPi, code coverage, CI.

IN TOTAL: ~8 hours of work.

# Extras.
* integration tests to make sure that everything is wired up correctly, and improve RedditBot tests.
* CLI tool for scraping subreddits.
* CLI tool for interacting with a running bot.
* updateable blacklisting / whitelisting.
* footers.
* receive commands. Allow specification of "owner". Owner can run commands such as pause, stop, stats, show blacklist, show whitelist, etc. Flexible enough that non-owner can send commands, different privilege levels. A subreddit can be blacklisted only by a moderator of that subreddit. Owner can whitelist/blacklist users & subreddits. Multiple owners?
* alarming, health status
