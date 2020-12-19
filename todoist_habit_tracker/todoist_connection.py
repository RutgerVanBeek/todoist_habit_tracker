import todoist


class TodoistConnection():

    def __init__(self, token):
        self.api = todoist.TodoistAPI(token)
        self._sync()
        self._projects = self.api.state['projects']
        self._tasks = self.api.state['items']
        self._labels= self.api.state['labels']

    @classmethod
    def from_config_file(cls, config_file):
        with open(config_file) as file:
            token = file.read()
        return cls(token)


    @property
    def projects(self):
        return self._projects

    @property
    def labels(self):
        return self._labels

    @property
    def tasks(self):
        return self._tasks

    @property
    def uncompleted_tasks(self):
        return self.filter_tasks(lambda task: task['checked'] == 0)

    def filter_tasks(self, filter_function):
        return list(filter(filter_function, self.tasks))

    def get_label_by_name(self, name):
        for label in self.labels:
            if label['name'] == name:
                return label
        raise KeyError('There is no label with the name {name}'.format(name=name))

    def add_task(self, task):
        # task['note'] += ' {automatic}'
        self.api.items.add(**task)
        # self.api.items.add(task['content'])

    def _sync(self):
        self.api.sync()
        self._projects = self.api.state['projects']
        self._tasks = self.api.state['items']
        self._labels= self.api.state['labels']

    def commit(self):
        self.api.commit()
