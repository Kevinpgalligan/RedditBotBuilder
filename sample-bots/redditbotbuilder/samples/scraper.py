from redditbotbuilder.bots import RedditBotBuilder

RedditBotBuilder.of_program_args("testingground4bots") \
    .with_comment_processing_action(lambda comment: print(comment.body))\
    .build()\
    .run()
