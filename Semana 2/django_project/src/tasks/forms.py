from django import forms


# Simple form for creating a task (no database, so plain Form).
class TaskForm(forms.Form):
    # Short title of the task.
    title = forms.CharField(
        max_length=120,
        label="Title",
        widget=forms.TextInput(attrs={"placeholder": "Task title"}),
    )
    # Optional long description of the task.
    description = forms.CharField(
        required=False,
        label="Description",
        widget=forms.Textarea(attrs={"rows": 3, "placeholder": "Task description"}),
    )
    # Current status of the task.
    status = forms.ChoiceField(
        label="Status",
        choices=[
            ("pending", "Pending"),
            ("in_progress", "In progress"),
            ("done", "Done"),
        ],
    )
    # Priority level of the task.
    priority = forms.ChoiceField(
        label="Priority",
        choices=[
            ("low", "Low"),
            ("medium", "Medium"),
            ("high", "High"),
        ],
    )
