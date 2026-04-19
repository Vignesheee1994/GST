from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

import streamlit as st


DATA_FILE = Path(__file__).with_name("tasks.json")


def load_tasks() -> list[dict]:
    if not DATA_FILE.exists():
        return []

    try:
        data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []

    if isinstance(data, list):
        return data
    return []


def save_tasks(tasks: list[dict]) -> None:
    DATA_FILE.write_text(json.dumps(tasks, indent=2), encoding="utf-8")


def add_task(title: str, details: str, due_date: str, priority: str) -> None:
    tasks = load_tasks()
    tasks.append(
        {
            "id": str(uuid4()),
            "title": title,
            "details": details,
            "due_date": due_date,
            "priority": priority,
            "done": False,
        }
    )
    save_tasks(tasks)


def update_task(task_id: str, done: bool) -> None:
    tasks = load_tasks()
    for task in tasks:
        if task["id"] == task_id:
            task["done"] = done
            break
    save_tasks(tasks)


def delete_task(task_id: str) -> None:
    tasks = [task for task in load_tasks() if task["id"] != task_id]
    save_tasks(tasks)


def clear_completed_tasks() -> None:
    tasks = [task for task in load_tasks() if not task["done"]]
    save_tasks(tasks)


st.set_page_config(page_title="To-Do List", page_icon=":memo:", layout="centered")

st.title("To-Do List")
st.caption("Keep track of tasks with priorities, due dates, and completion status.")

with st.form("add_task_form", clear_on_submit=True):
    st.subheader("Add a Task")
    title = st.text_input("Task title")
    details = st.text_area("Details", placeholder="Optional notes")
    due_date = st.date_input("Due date", value=None)
    priority = st.selectbox("Priority", ["Low", "Medium", "High"], index=1)
    submitted = st.form_submit_button("Add Task")

    if submitted:
        if title.strip():
            add_task(
                title=title.strip(),
                details=details.strip(),
                due_date=due_date.isoformat() if due_date else "",
                priority=priority,
            )
            st.success("Task added.")
            st.rerun()
        else:
            st.warning("Enter a task title before adding it.")


tasks = load_tasks()

total_tasks = len(tasks)
completed_tasks = sum(task["done"] for task in tasks)
pending_tasks = total_tasks - completed_tasks

col1, col2, col3 = st.columns(3)
col1.metric("Total", total_tasks)
col2.metric("Pending", pending_tasks)
col3.metric("Completed", completed_tasks)

st.divider()

filter_option = st.radio(
    "Show",
    options=["All", "Pending", "Completed"],
    horizontal=True,
)

filtered_tasks = tasks
if filter_option == "Pending":
    filtered_tasks = [task for task in tasks if not task["done"]]
elif filter_option == "Completed":
    filtered_tasks = [task for task in tasks if task["done"]]

if filtered_tasks:
    for task in filtered_tasks:
        with st.container(border=True):
            left, right = st.columns([0.8, 0.2])

            with left:
                done = st.checkbox(
                    task["title"],
                    value=task["done"],
                    key=f"done_{task['id']}",
                )
                if done != task["done"]:
                    update_task(task["id"], done)
                    st.rerun()

                meta = [f"Priority: {task['priority']}"]
                if task["due_date"]:
                    meta.append(f"Due: {task['due_date']}")
                st.caption(" | ".join(meta))

                if task["details"]:
                    st.write(task["details"])

            with right:
                if st.button("Delete", key=f"delete_{task['id']}", use_container_width=True):
                    delete_task(task["id"])
                    st.rerun()
else:
    st.info("No tasks found for this view.")

st.divider()

if st.button("Clear Completed Tasks", type="secondary", use_container_width=True):
    clear_completed_tasks()
    st.rerun()
