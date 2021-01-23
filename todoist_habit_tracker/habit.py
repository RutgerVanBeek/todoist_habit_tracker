import re


class Habit:

    def __init__(self, task, api, label_id):
        self.api = api
        effective_str = re.search('\[(.*)\]', task['content']).group(1)
        self.daily = 'daily' in effective_str
        self.later = 'later' in effective_str
        self.task = task
        # self.task['content'] = re.sub('\[(.*)\]', '', self.task['content'])
        self.label_id = label_id
        print(len(re.sub('\[(.*)\]', '', self.task['content'])))

    def create_new(self, due='today'):
        task = {
            'content': re.sub('\[(.*)\]', '', self.task['content']).strip(),
            'project_id': self.task['project_id'],
            'priority': self.task['priority']
        }
        task['labels'] = [label for label in self.task['labels'] if label != self.label_id]
        task['due'] = {'string': due}
        # also copy subtasks
        subtasks = self.api.filter_tasks(lambda x: self.task['id'] == x['parent_id'])
        new = self.api.add_task(task)
        # get subtasks
        for subtask in subtasks:
            # copy task
            new_task = {'content': subtask['content'], 'project_id': subtask['project_id'],
                        'priority': subtask['priority']}
            new_task['parent_id'] = new['id']
            self.api.add_task(new_task)

    def equal_tasks(self):
        def is_equal(task):
            return task['content'] == re.sub('\[(.*)\]', '', self.task['content']).strip() and \
                task['project_id'] == self.task['project_id'] and self.label_id not in task['labels']
        return self.api.filter_tasks(is_equal)

    def determine_action(self):
        flag = False
        print(self.equal_tasks())
        for task in self.equal_tasks():
            print('due is')
            print(task['due'])
            if task['due'] == 'today':
                flag = True
            else:
                if not self.later:
                    self.api.delete_task(task)
        if not flag:
            self.create_new(due='today')

    def __str__(self):
        return 'habit: {0}'.format(self.task['content'])
