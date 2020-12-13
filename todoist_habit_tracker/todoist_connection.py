import todoist


class TodoistConnection():

    def __init__(self, token):
        self.api = todoist.TodoistAPI(token)
        self._sync()
        self._projects = self.api.state['projects']
        self._tasks = self.api.state['items']

    @classmethod
    def from_config_file(cls, config_file):
        with open(config_file) as file:
            token = file.read()
        return cls(token)


    @property
    def projects(self):
        return self._projects

    @property
    def tasks(self):
        return self._tasks

    @property
    def uncompleted_tasks(self):
        return self.filter_tasks(lambda task: task['checked'] == 0)

    def filter_tasks(self, filter_function):
        return list(filter(filter_function, self.api.state['items']))

    def _sync(self):
        self.api.sync()
