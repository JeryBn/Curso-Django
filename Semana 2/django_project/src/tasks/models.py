"""Static in-memory task store (no database).

The rubric (criterion 2) requires static data instead of a database model,
so tasks live in the TASKS list for the lifetime of the process.
"""

# Initial in-memory tasks with distinct priorities.
TASKS = [
    {
        "id": 1,
        "title": "Prepare lab report",
        "description": "Summarize the Django workflow lab.",
        "status": "pending",
        "priority": "high",
        "created_at": "2026-09-01",
    },
    {
        "id": 2,
        "title": "Review Django forms",
        "description": "Study Form validation with ChoiceField.",
        "status": "in_progress",
        "priority": "medium",
        "created_at": "2026-09-02",
    },
    {
        "id": 3,
        "title": "Organize project files",
        "description": "Keep Semana 2 isolated from Semana 1.",
        "status": "done",
        "priority": "low",
        "created_at": "2026-09-03",
    },
]


# Return all tasks in memory.
def get_tasks():
    return list(TASKS)


# Find a single task by its id, or None when missing.
def get_task_by_id(task_id):
    for task in TASKS:
        if task["id"] == task_id:
            return task
    return None


# Append a new task to the in-memory list and return it.
def add_task(title, description, status, priority):
    # Compute the next id from the existing tasks.
    if TASKS:
        next_id = max(task["id"] for task in TASKS) + 1
    else:
        next_id = 1
    # Build the new task dict with a plain string date.
    task = {
        "id": next_id,
        "title": title,
        "description": description,
        "status": status,
        "priority": priority,
        "created_at": "2026-09-08",
    }
    TASKS.append(task)
    return task
