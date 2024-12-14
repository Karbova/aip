class TaskManager:
    def __init__(self):
        self.tasks = []
        self.next_id = 1

    def add_task(self, title, description, assignee, deadline):
        if not all([title, description, assignee, deadline]):
            raise ValueError("Все поля задачи должны быть заполнены")
        task = {
            "id": self.next_id,
            "title": title,
            "description": description,
            "assignee": assignee,
            "deadline": deadline,
            "status": "Не начата",
        }
        self.tasks.append(task)
        self.next_id += 1
        return task

    def mark_completed(self, task_id):
        task = self.get_task_by_id(task_id)
        task["status"] = "Выполнена"

    def mark_in_progress(self, task_id):
        task = self.get_task_by_id(task_id)
        task["status"] = "В процессе"

    def delete_task(self, task_id):
        self.tasks = [task for task in self.tasks if task["id"] != task_id]

    def get_task_by_id(self, task_id):
        for task in self.tasks:
            if task["id"] == task_id:
                return task
        raise ValueError(f"Задача с ID {task_id} не найдена")

    def save_to_json(self, filename):
        import json

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.tasks, f, ensure_ascii=False, indent=4)

    def load_from_json(self, filename):
        import json

        with open(filename, "r", encoding="utf-8") as f:
            self.tasks = json.load(f)
        self.next_id = max(task["id"] for task in self.tasks) + 1 if self.tasks else 1
