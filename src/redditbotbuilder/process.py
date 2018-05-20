
class ItemProcessor:

    def __init__(self, actions, processing_queue):
        self.actions = actions
        self.processing_queue = processing_queue

    def run(self):
        # todo catch exceptions here?
        while True:
            print("processor is getting")
            item, action_ids = self.processing_queue.get()
            print("got an item boss!", item, action_ids)
            actions_to_execute = [action for action in self.actions if action.id in action_ids]
            print("actions to execute:", actions_to_execute)
            for action in actions_to_execute:
                try:
                    action.execute(item)
                except Exception as e:
                    # Never stop processing comments.
                    print(e)