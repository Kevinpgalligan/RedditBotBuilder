# MVP
* think through possible loop-breaking errors (e.g. can't get bot's own name due to rate-limiting).
* see what methods on the models require a call to the API, make sure that they are not being used if unnecessary (eg user hasn't implemented method that requires them).
* think through extension of interface, e.g. adding more data that can be passed cleanly to the bot. As of now, can't add new data without breaking old interface. So should probably pass only a Data object or Input object for each method, which can be expanded with new attributes. Also, think really hard about the names, since they can't be changed later.
* manual tests: all scenarios where something gets deleted. reply to comment of bot without mentioning it, just the name of the bot, see what happens. And fix these edge cases.
* integration tests to make sure that everything is wired up correctly, and improve RedditBot tests.
* limit number of interactions (by user, by thread, etc). And allow this to be customised.
* whitelisting (+ add more to the blacklist on start-up).
* set up logging (customisable).
* specify location to save state (logs, blacklist, post count, etc).
* saving state (+ read previous state on start-up).
* different methods of providing credentials.
* Scanner bot, rather than a bot that just replies to mentions.
* go through all inline TODOs and fix them.
* All of the soft stuff. Documentation, PyPi, code coverage, CI.

# Extras.
* CLI tool for scraping subreddits.
* CLI tool for interacting with a running bot.
* updateable blacklisting / whitelisting.
* footers.
* receive commands. Allow specification of "owner". Owner can run commands such as pause, stop, stats, show blacklist, show whitelist, etc. Flexible enough that non-owner can send commands, different privilege levels. A subreddit can be blacklisted only by a moderator of that subreddit. Owner can whitelist/blacklist users & subreddits. Multiple owners?
* alarming, health status
