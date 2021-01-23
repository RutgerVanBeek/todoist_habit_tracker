import todoist


class TodoistConnection():

    def __init__(self, token):
        self.api = todoist.TodoistAPI(token)
        self._sync()
        self._projects = self.api.state['projects']
        self._tasks = self.api.state['items']
        self._labels = self.api.state['labels']

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

    def get_project_by_name(self, name):
        for project in self.projects:
            if project['name'] == name:
                return project
        raise KeyError('There is no project with the name {name}'.format(name=name))

    def add_task(self, task):
        # task['content'] += ' {automatic}'
        return self.api.items.add(**task)

    def delete_task(self, task):
        self.delete_task_id(task['id'])

    def delete_task_id(self, task_id):
        self.api.items.delete(task_id)

    def _sync(self):
        self.api.sync()

    def _reset(self):
        self.api.reset_state()
        self.api.sync()
        self._projects = self.api.state['projects']
        self._tasks = self.api.state['items']
        self._labels = self.api.state['labels']

    def commit(self):
        self.api.commit()
