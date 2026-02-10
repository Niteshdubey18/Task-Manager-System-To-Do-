import tkinter as tk
from tkinter import messagebox
import os

FILE_NAME = "tasks.txt"


class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("To-Do App (Python GUI)")
        self.root.geometry("450x500")
        self.root.resizable(False, False)

        # Heading
        title = tk.Label(root, text="✅ To-Do Application", font=("Arial", 18, "bold"))
        title.pack(pady=10)

        # Entry box
        self.task_entry = tk.Entry(root, font=("Arial", 12), width=30)
        self.task_entry.pack(pady=10)

        # Buttons frame
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=5)

        add_btn = tk.Button(btn_frame, text="Add Task", width=12, command=self.add_task)
        add_btn.grid(row=0, column=0, padx=5)

        done_btn = tk.Button(btn_frame, text="Mark Done", width=12, command=self.mark_done)
        done_btn.grid(row=0, column=1, padx=5)

        delete_btn = tk.Button(btn_frame, text="Delete Task", width=12, command=self.delete_task)
        delete_btn.grid(row=0, column=2, padx=5)

        # Task listbox
        self.task_listbox = tk.Listbox(root, font=("Arial", 12), width=45, height=15)
        self.task_listbox.pack(pady=15)

        # Save button
        save_btn = tk.Button(root, text="Save Tasks", width=20, command=self.save_tasks)
        save_btn.pack(pady=10)

        # Load tasks on start
        self.load_tasks()

    def add_task(self):
        task = self.task_entry.get().strip()
        if task == "":
            messagebox.showwarning("Warning", "Task cannot be empty!")
            return
        self.task_listbox.insert(tk.END, task)
        self.task_entry.delete(0, tk.END)

    def delete_task(self):
        try:
            selected_index = self.task_listbox.curselection()[0]
            self.task_listbox.delete(selected_index)
        except IndexError:
            messagebox.showwarning("Warning", "Please select a task to delete.")

    def mark_done(self):
        try:
            selected_index = self.task_listbox.curselection()[0]
            task = self.task_listbox.get(selected_index)

            if task.startswith("✅ "):
                messagebox.showinfo("Info", "Task is already marked as done.")
                return

            self.task_listbox.delete(selected_index)
            self.task_listbox.insert(selected_index, "✅ " + task)
        except IndexError:
            messagebox.showwarning("Warning", "Please select a task to mark done.")

    def save_tasks(self):
        tasks = self.task_listbox.get(0, tk.END)
        with open(FILE_NAME, "w", encoding="utf-8") as file:
            for task in tasks:
                file.write(task + "\n")
        messagebox.showinfo("Saved", "Tasks saved successfully!")

    def load_tasks(self):
        if os.path.exists(FILE_NAME):
            with open(FILE_NAME, "r", encoding="utf-8") as file:
                for line in file:
                    task = line.strip()
                    if task:
                        self.task_listbox.insert(tk.END, task)


if __name__ == "__main__":
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()