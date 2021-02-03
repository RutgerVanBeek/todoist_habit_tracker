import re


class Habit:

    def __init__(self, task, api, label_id, weekly_label_id):
        self.api = api
        effective_str = re.search('\[(.*)\]', task['content']).group(1)
        self.daily = 'daily' in effective_str
        self.later = 'later' in effective_str
        self.weekly = 'weekly' in effective_str
        self.task = task
        self.content = re.sub('\[(.*)\]', '', self.task['content']).strip()
        self.label_id = label_id
        self.weekly_label_id = weekly_label_id

    def create_new(self, due='today'):
        task = {
            'content': self.content,
            'project_id': self.task['project_id'],
            'priority': self.task['priority']
        }
        task['labels'] = [label for label in self.task['labels'] if label != self.label_id]
        task['due'] = {'string': due}
        task['parent_id'] = None
        subtasks = self.api.filter_tasks(lambda x: self.task['id'] == x['parent_id'])
        new = self.api.add_task(task)
        for subtask in subtasks:
            new_task = {'content': subtask['content'], 'project_id': subtask['project_id'],
                        'priority': subtask['priority']}
            new_task['parent_id'] = new['id']
            self.api.add_task(new_task)

    def create_new_weekly(self):
        print('here weekly')
        task = {
            'content': self.content,
            'project_id': self.task['project_id'],
            'priority': self.task['priority']
        }
        task['labels'] = [label for label in self.task['labels'] if label != self.label_id]
        task['labels'].append(self.weekly_label_id)
        task['parent_id'] = None
        subtasks = self.api.filter_tasks(lambda x: self.task['id'] == x['parent_id'])
        new = self.api.add_task(task)
        for subtask in subtasks:
            new_task = {'content': subtask['content'], 'project_id': subtask['project_id'],
                        'priority': subtask['priority']}
            new_task['parent_id'] = new['id']
            self.api.add_task(new_task)

    def equal_tasks(self):
        def is_equal(task):
            return task['content'] == self.content and \
                task['project_id'] == self.task['project_id'] and self.label_id not in task['labels']
        return self.api.filter_tasks(is_equal)

    def determine_action(self):
        if self.daily:
            flag = False
            for task in self.equal_tasks():
                if task['due'] == 'today':
                    flag = True
                else:
                    if not self.later:
                        self.api.delete_task(task)
            if not flag:
                self.create_new(due='today')
        if self.weekly:
            self.create_new_weekly()

    def done(self):
        if self.weekly:
            return False
        comp = self.api.completed_tasks
        contents = [re.sub('@.* ', '', c['content']) for c in comp]
        contents = [re.sub('@.*', '', c).strip() for c in contents]
        return self.content in contents

    def __str__(self):
        return self.content
