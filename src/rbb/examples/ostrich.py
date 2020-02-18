from rbb import RedditBot
import random

FACTS = [
    "ostriches may be taller than 1.6m, but I'm not sure.",
    "ostriches have black feathers... I think."
]

class OstrichBot(RedditBot):

    def reply_to_mention(self, username, text):
        return "Hi {}, here's the ostrich fact you requested: {}".format(
            username,
            random.choice(FACTS))

if __name__ == "__main__":
    OstrichBot().run()
