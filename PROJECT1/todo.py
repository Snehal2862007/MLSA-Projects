import json
import os
from datetime import date, datetime, timedelta
from tkinter import Tk, Frame, Label, Entry, StringVar, END, W, E, N, S
from tkinter import messagebox
from tkinter.font import Font
from tkinter import ttk


class Task:
    def __init__(self, title, priority, difficulty, due_date, status="Pending"):
        self.title = title.strip()
        self.priority = priority
        self.difficulty = difficulty
        self.due_date = due_date
        self.status = status

    def to_dict(self):
        return {
            "title": self.title,
            "priority": self.priority,
            "difficulty": self.difficulty,
            "due_date": self.due_date,
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, raw):
        return cls(
            title=raw.get("title", ""),
            priority=raw.get("priority", "Medium"),
            difficulty=raw.get("difficulty", "Medium"),
            due_date=raw.get("due_date", ""),
            status=raw.get("status", "Pending"),
        )


class TaskManager:
    STORAGE_FILE = os.path.join(os.path.dirname(__file__), "tasks.json")

    def __init__(self):
        self.tasks = []
        self.streak_count = 0
        self.last_completed_date = None
        self.load_tasks()

    def add_task(self, task):
        if not task.title:
            raise ValueError("Task title cannot be empty.")

        auto_subtasks = self._generate_auto_subtasks(task)
        self.tasks.append(task)
        if auto_subtasks:
            self.tasks.extend(auto_subtasks)
        self.save_tasks()
        return auto_subtasks

    def delete_task(self, index):
        if 0 <= index < len(self.tasks):
            self.tasks.pop(index)
            self.save_tasks()

    def update_task(self, index, task):
        if 0 <= index < len(self.tasks):
            self.tasks[index] = task
            self.save_tasks()

    def mark_completed(self, index):
        if 0 <= index < len(self.tasks):
            self.tasks[index].status = "Completed"
            self._update_streak()
            self.save_tasks()

    def filter_tasks(self, status_filter="All"):
        if status_filter == "Pending":
            return [task for task in self.tasks if task.status == "Pending"]
        if status_filter == "Completed":
            return [task for task in self.tasks if task.status == "Completed"]
        return self.tasks

    def get_total_effort(self):
        effort_map = {"Easy": 1, "Medium": 2, "Hard": 3}
        return sum(effort_map.get(task.difficulty, 2) for task in self.tasks if task.status == "Pending")

    def get_mood_suggestions(self, mood):
        suggestions = []
        if mood == "Tired":
            suggestions = [task.title for task in self.tasks if task.status == "Pending" and task.difficulty == "Easy"]
        elif mood == "Energetic":
            suggestions = [task.title for task in self.tasks if task.status == "Pending" and task.difficulty == "Hard"]
        else:
            suggestions = [task.title for task in self.tasks if task.status == "Pending" and task.difficulty == "Medium"]

        if not suggestions:
            suggestions = [task.title for task in self.tasks if task.status == "Pending"]
        return suggestions[:5]

    def save_tasks(self):
        data = {
            "tasks": [task.to_dict() for task in self.tasks],
            "streak_count": self.streak_count,
            "last_completed_date": self.last_completed_date,
        }
        with open(self.STORAGE_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2)

    def load_tasks(self):
        if not os.path.exists(self.STORAGE_FILE):
            self._initialize_storage()
            return

        try:
            with open(self.STORAGE_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)
            raw_tasks = data.get("tasks", [])
            self.tasks = [Task.from_dict(raw) for raw in raw_tasks]
            self.streak_count = data.get("streak_count", 0)
            self.last_completed_date = data.get("last_completed_date")
        except (ValueError, json.JSONDecodeError):
            self._initialize_storage()

    def _initialize_storage(self):
        self.tasks = []
        self.streak_count = 0
        self.last_completed_date = None
        self.save_tasks()

    def _generate_auto_subtasks(self, task):
        keywords = ["project", "assignment"]
        lowercase_title = task.title.lower()
        if any(keyword in lowercase_title for keyword in keywords):
            base = task.title
            subtasks = [
                Task(f"{base} - part 1", task.priority, task.difficulty, task.due_date),
                Task(f"{base} - part 2", task.priority, task.difficulty, task.due_date),
            ]
            return subtasks
        return []

    def _update_streak(self):
        today = date.today().isoformat()
        if self.last_completed_date == today:
            return

        if self.last_completed_date:
            last_date = date.fromisoformat(self.last_completed_date)
            if last_date == date.today() - timedelta(days=1):
                self.streak_count += 1
            else:
                self.streak_count = 1
        else:
            self.streak_count = 1

        self.last_completed_date = today


class SmartTodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart To-Do List Pro")
        self.root.geometry("900x620")
        self.root.resizable(False, False)
        self.root.configure(bg="#eaf0ff")

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("Header.TLabel", font=("Segoe UI", 18, "bold"), background="#3B75FF", foreground="white")
        self.style.configure("Section.TLabel", font=("Segoe UI", 10, "bold"), background="#f3f5ff", foreground="#333333")
        self.style.configure("Card.TFrame", background="white")
        self.style.configure("Accent.TLabel", font=("Segoe UI", 10, "bold"), background="#f3f5ff", foreground="#1f305d")
        self.style.configure("Stat.TLabel", font=("Segoe UI", 11, "bold"), background="white", foreground="#1f3a72")
        self.style.configure("StatValue.TLabel", font=("Segoe UI", 14, "bold"), background="white", foreground="#3B75FF")
        self.style.configure("Action.TButton", font=("Segoe UI", 10, "bold"), background="#3B75FF", foreground="white", borderwidth=0, focusthickness=3, focuscolor="#3755c7")
        self.style.map("Action.TButton", background=[("active", "#2f64e6")])
        self.style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background="#d8e2ff", foreground="#1f305d")
        self.style.configure("Treeview", font=("Segoe UI", 10), rowheight=26, fieldbackground="white", background="white", foreground="#1f3a72", borderwidth=0, relief="flat")
        self.style.map("Treeview", background=[("selected", "#b3d0ff")], foreground=[("selected", "#0d264f")])

        self.manager = TaskManager()
        self.selected_index = None

        self._create_widgets()
        self._load_table()
        self._update_status_labels()

        self.root.bind("<Return>", lambda event: self.add_task())

    def _create_widgets(self):
        header_frame = Frame(self.root, bg="#3B75FF", padx=12, pady=14)
        header_frame.grid(row=0, column=0, sticky=W + E)
        ttk.Label(header_frame, text="Smart To-Do List Pro", style="Header.TLabel").grid(row=0, column=0, sticky=W)

        entry_frame = Frame(self.root, bg="#f3f5ff", padx=14, pady=12, bd=0)
        entry_frame.grid(row=1, column=0, sticky=W + E, padx=10, pady=(10, 0))

        Label(entry_frame, text="Task:", background="#f3f5ff", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky=W, pady=4)
        self.task_entry = Entry(entry_frame, width=36, font=("Segoe UI", 10), relief="flat", bg="white")
        self.task_entry.grid(row=0, column=1, columnspan=3, sticky=W, padx=4, pady=4)

        Label(entry_frame, text="Priority:", background="#f3f5ff", font=("Segoe UI", 10, "bold")).grid(row=1, column=0, sticky=W, pady=4)
        self.priority_var = StringVar(value="Medium")
        self.priority_combo = ttk.Combobox(entry_frame, textvariable=self.priority_var, values=["High", "Medium", "Low"], state="readonly", width=14)
        self.priority_combo.grid(row=1, column=1, sticky=W, padx=4, pady=4)

        Label(entry_frame, text="Difficulty:", background="#f3f5ff", font=("Segoe UI", 10, "bold")).grid(row=1, column=2, sticky=W, pady=4)
        self.difficulty_var = StringVar(value="Medium")
        self.difficulty_combo = ttk.Combobox(entry_frame, textvariable=self.difficulty_var, values=["Easy", "Medium", "Hard"], state="readonly", width=14)
        self.difficulty_combo.grid(row=1, column=3, sticky=W, padx=4, pady=4)

        Label(entry_frame, text="Due Date (YYYY-MM-DD):", background="#f3f5ff", font=("Segoe UI", 10, "bold")).grid(row=2, column=0, sticky=W, pady=4)
        self.due_date_entry = Entry(entry_frame, width=16, font=("Segoe UI", 10), relief="flat", bg="white")
        self.due_date_entry.grid(row=2, column=1, sticky=W, padx=4, pady=4)

        Label(entry_frame, text="Mood:", background="#f3f5ff", font=("Segoe UI", 10, "bold")).grid(row=2, column=2, sticky=W, pady=4)
        self.mood_var = StringVar(value="Normal")
        self.mood_combo = ttk.Combobox(entry_frame, textvariable=self.mood_var, values=["Tired", "Energetic", "Normal"], state="readonly", width=14)
        self.mood_combo.grid(row=2, column=3, sticky=W, padx=4, pady=4)
        self.mood_combo.bind("<<ComboboxSelected>>", lambda _: self._update_suggestions())

        button_frame = Frame(self.root, bg="#eaf0ff", padx=10, pady=8)
        button_frame.grid(row=2, column=0, sticky=W + E, padx=10, pady=(8, 0))

        ttk.Button(button_frame, text="Add Task", style="Action.TButton", command=self.add_task).grid(row=0, column=0, padx=6, pady=6)
        ttk.Button(button_frame, text="Update Task", style="Action.TButton", command=self.update_task).grid(row=0, column=1, padx=6, pady=6)
        ttk.Button(button_frame, text="Delete Task", style="Action.TButton", command=self.delete_task).grid(row=0, column=2, padx=6, pady=6)
        ttk.Button(button_frame, text="Mark Completed", style="Action.TButton", command=self.mark_completed).grid(row=0, column=3, padx=6, pady=6)
        ttk.Button(button_frame, text="Clear Selection", style="Action.TButton", command=self._clear_selection).grid(row=0, column=4, padx=6, pady=6)

        filter_frame = Frame(self.root, bg="#f3f5ff", padx=14, pady=12)
        filter_frame.grid(row=3, column=0, sticky=W + E, padx=10, pady=(0, 10))

        Label(filter_frame, text="Filter:", background="#f3f5ff", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky=W)
        self.filter_var = StringVar(value="All")
        filter_options = ["All", "Pending", "Completed"]
        self.filter_combo = ttk.Combobox(filter_frame, textvariable=self.filter_var, values=filter_options, state="readonly", width=14)
        self.filter_combo.grid(row=0, column=1, padx=6)
        self.filter_combo.bind("<<ComboboxSelected>>", lambda _: self._load_table())

        Label(filter_frame, text="Mood-based Suggestions:", background="#f3f5ff", font=("Segoe UI", 10, "bold")).grid(row=0, column=2, sticky=W, padx=(24, 4))
        self.suggestion_label = Label(filter_frame, text="", bg="#f3f5ff", fg="#1f4d92", font=("Segoe UI", 10))
        self.suggestion_label.grid(row=0, column=3, sticky=W)

        self.count_frame = Frame(filter_frame, bg="#f3f5ff")
        self.count_frame.grid(row=1, column=0, columnspan=4, sticky=W, pady=(10, 0))
        self.total_label = Label(self.count_frame, text="Total Tasks: 0", bg="white", fg="#1f3a72", font=("Segoe UI", 10, "bold"), padx=12, pady=8, bd=1, relief="groove")
        self.total_label.grid(row=0, column=0, padx=(0, 12))
        self.pending_label = Label(self.count_frame, text="Pending: 0", bg="white", fg="#1f3a72", font=("Segoe UI", 10, "bold"), padx=12, pady=8, bd=1, relief="groove")
        self.pending_label.grid(row=0, column=1, padx=(0, 12))
        self.completed_label = Label(self.count_frame, text="Completed: 0", bg="white", fg="#1f3a72", font=("Segoe UI", 10, "bold"), padx=12, pady=8, bd=1, relief="groove")
        self.completed_label.grid(row=0, column=2, padx=(0, 12))

        Label(filter_frame, text="Total Effort:", background="#f3f5ff", font=("Segoe UI", 10, "bold")).grid(row=2, column=0, sticky=W, pady=6)
        self.effort_label = Label(filter_frame, text="0 points", bg="#f3f5ff", fg="#1f3a72", font=("Segoe UI", 10, "bold"))
        self.effort_label.grid(row=2, column=1, sticky=W, pady=6)

        Label(filter_frame, text="Streak:", background="#f3f5ff", font=("Segoe UI", 10, "bold")).grid(row=2, column=2, sticky=W, padx=(24, 4), pady=6)
        self.streak_label = Label(filter_frame, text="0 days", bg="#f3f5ff", fg="#1f3a72", font=("Segoe UI", 10, "bold"))
        self.streak_label.grid(row=2, column=3, sticky=W, pady=6)

        table_frame = Frame(self.root, bg="#f3f5ff", padx=10, pady=10)
        table_frame.grid(row=4, column=0, sticky=N + S + W + E)
        self.root.grid_rowconfigure(4, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        card_frame = Frame(table_frame, bg="white", bd=1, relief="solid")
        card_frame.grid(row=0, column=0, sticky=N + S + W + E)
        card_frame.grid_rowconfigure(0, weight=1)
        card_frame.grid_columnconfigure(0, weight=1)

        columns = ("Task", "Priority", "Difficulty", "Due Date", "Status")
        self.tree = ttk.Treeview(card_frame, columns=columns, show="headings", height=16)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor=W, width=170 if col == "Task" else 110)

        self.tree.tag_configure("pending_high", background="#ffe7e7", foreground="#7d1c1c")
        self.tree.tag_configure("pending_medium", background="#fff7e0", foreground="#6a4f1f")
        self.tree.tag_configure("pending_low", background="#e8f3ff", foreground="#1d4d7a")
        self.tree.tag_configure("completed_high", background="#ffd9df", foreground="#7d1c1c")
        self.tree.tag_configure("completed_medium", background="#def7e3", foreground="#1f603f")
        self.tree.tag_configure("completed_low", background="#d9edff", foreground="#1d4d7a")
        self.tree.grid(row=0, column=0, sticky=N + S + W + E)
        self.tree.bind("<<TreeviewSelect>>", self._on_task_select)
        self.tree.bind("<Double-1>", self._on_task_double_click)

        scrollbar = ttk.Scrollbar(card_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky=N + S)

    def add_task(self):
        title = self.task_entry.get().strip()
        priority = self.priority_var.get()
        difficulty = self.difficulty_var.get()
        due_date = self.due_date_entry.get().strip()
        if due_date and not self._is_valid_date(due_date):
            messagebox.showwarning("Invalid Date", "Enter due date as YYYY-MM-DD or leave blank.")
            return

        new_task = Task(title, priority, difficulty, due_date)
        try:
            auto_subtasks = self.manager.add_task(new_task)
            if auto_subtasks:
                messagebox.showinfo("Auto Task Splitter", "A large task was detected and subtasks were added automatically.")
            self._reset_inputs()
            self._load_table()
            self._update_status_labels()
        except ValueError as error:
            messagebox.showwarning("Invalid Task", str(error))

    def delete_task(self):
        if self.selected_index is None:
            messagebox.showwarning("No Selection", "Please select a task to delete.")
            return
        self.manager.delete_task(self.selected_index)
        self.selected_index = None
        self._reset_inputs()
        self._load_table()
        self._update_status_labels()

    def update_task(self):
        if self.selected_index is None:
            messagebox.showwarning("No Selection", "Please select a task to update.")
            return

        title = self.task_entry.get().strip()
        priority = self.priority_var.get()
        difficulty = self.difficulty_var.get()
        due_date = self.due_date_entry.get().strip()
        if due_date and not self._is_valid_date(due_date):
            messagebox.showwarning("Invalid Date", "Enter due date as YYYY-MM-DD or leave blank.")
            return

        updated_task = Task(title, priority, difficulty, due_date, self.manager.tasks[self.selected_index].status)
        self.manager.update_task(self.selected_index, updated_task)
        self._reset_inputs()
        self.selected_index = None
        self._load_table()
        self._update_status_labels()

    def mark_completed(self):
        if self.selected_index is None:
            messagebox.showwarning("No Selection", "Please select a task to mark completed.")
            return
        self.manager.mark_completed(self.selected_index)
        self._reset_inputs()
        self.selected_index = None
        self._load_table()
        self._update_status_labels()

    def _load_table(self):
        self.tree.delete(*self.tree.get_children())
        filtered_tasks = self.manager.filter_tasks(self.filter_var.get())
        for idx, task in enumerate(filtered_tasks):
            priority_tag = task.priority.lower()
            status_tag = "completed" if task.status == "Completed" else "pending"
            tag = f"{status_tag}_{priority_tag}"
            self.tree.insert("", END, iid=str(idx), values=(task.title, task.priority, task.difficulty, task.due_date, task.status), tags=(tag,))
        self._update_suggestions()

    def _on_task_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return

        row_index = int(selected[0])
        filtered_tasks = self.manager.filter_tasks(self.filter_var.get())
        selected_task = filtered_tasks[row_index]
        self.selected_index = self.manager.tasks.index(selected_task)

        self.task_entry.delete(0, END)
        self.task_entry.insert(0, selected_task.title)
        self.priority_var.set(selected_task.priority)
        self.difficulty_var.set(selected_task.difficulty)
        self.due_date_entry.delete(0, END)
        self.due_date_entry.insert(0, selected_task.due_date)

    def _update_status_labels(self):
        total_effort = self.manager.get_total_effort()
        self.effort_label.configure(text=f"{total_effort} effort points")
        self.streak_label.configure(text=f"{self.manager.streak_count} days")
        self._update_counts()

    def _update_counts(self):
        total = len(self.manager.tasks)
        pending = len([task for task in self.manager.tasks if task.status == "Pending"])
        completed = len([task for task in self.manager.tasks if task.status == "Completed"])
        self.total_label.configure(text=f"Total Tasks: {total}")
        self.pending_label.configure(text=f"Pending: {pending}")
        self.completed_label.configure(text=f"Completed: {completed}")

    def _update_suggestions(self):
        mood = self.mood_var.get()
        suggestions = self.manager.get_mood_suggestions(mood)
        if suggestions:
            self.suggestion_label.configure(text=" | ".join(suggestions[:3]))
        else:
            self.suggestion_label.configure(text="No pending tasks yet.")

    def _reset_inputs(self):
        self.task_entry.delete(0, END)
        self.priority_var.set("Medium")
        self.difficulty_var.set("Medium")
        self.due_date_entry.delete(0, END)
        self.mood_var.set("Normal")
        self.selected_index = None
        try:
            self.tree.selection_remove(self.tree.selection())
        except Exception:
            pass
        self.task_entry.focus_set()

    def _clear_selection(self):
        self.selected_index = None
        try:
            self.tree.selection_remove(self.tree.selection())
        except Exception:
            pass
        self._reset_inputs()

    def _on_task_double_click(self, event):
        self._on_task_select(event)
        self.task_entry.focus_set()

    @staticmethod
    def _is_valid_date(value):
        try:
            datetime.strptime(value, "%Y-%m-%d")
            return True
        except ValueError:
            return False


if __name__ == "__main__":
    root = Tk()
    app = SmartTodoApp(root)
    root.mainloop()

