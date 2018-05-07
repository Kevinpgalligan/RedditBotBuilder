import redditbotbuilder

redditbotbuilder.of_program_args("testingground4bots")\
    .with_comment_processing(lambda comment: print(comment.body))\
    .build()\
    .run()
