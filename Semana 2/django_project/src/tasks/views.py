from django.contrib import messages
from django.shortcuts import redirect, render

from .forms import TaskForm
from .models import get_tasks, add_task


# Display the list of all in-memory tasks.
def task_list(request):
    # Retrieve tasks from the static store.
    tasks = get_tasks()
    # Count tasks for the template context.
    total = len(tasks)
    # Render the list template with tasks and total in the context.
    return render(request, "tasks/task_list.html", {"tasks": tasks, "total": total})


# Create a new task in memory with a simple Form.
def task_create(request):
    # Handle form submission on POST.
    if request.method == "POST":
        form = TaskForm(request.POST)
        # Validate with standard Django validation.
        if form.is_valid():
            # Add the cleaned data to the static list.
            task = add_task(
                title=form.cleaned_data["title"],
                description=form.cleaned_data["description"],
                status=form.cleaned_data["status"],
                priority=form.cleaned_data["priority"],
            )
            # Show a success message on the list page.
            messages.success(request, f'Task "{task["title"]}" created successfully.')
            return redirect("tasks:task_list")
    else:
        # Show an empty form on GET.
        form = TaskForm()
    # Render the form template with the form in the context.
    return render(request, "tasks/task_form.html", {"form": form})
