from multiprocessing import Queue

class RedditItemQueue:

    def __init__(self):
        self.queue = Queue()

    def put(self, item, *rest):
        set_reddit(item, None)
        return self.queue.put((item, *rest))

    def get(self, reddit):
        item, *rest = self.queue.get()
        set_reddit(item, reddit)
        return (item, *rest)

def set_reddit(item, reddit):
    # todo this
    return item