import tkinter as tk
from tkinter import ttk, messagebox
import random
import json
import os

class RandomTaskGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Task Generator - Снежана Хисматуллина")
        self.root.geometry("550x550")
        self.root.resizable(True, True)

        # Предопределённые задачи
        self.predefined_tasks = [
            ("Прочитать статью", "учёба"),
            ("Сделать зарядку", "спорт"),
            ("Написать код", "работа"),
            ("Выпить стакан воды", "спорт"),
            ("Повторить лекцию", "учёба"),
            ("Сделать план на день", "работа"),
            ("Помыть посуду", "работа"),
            ("Пробежка 1 км", "спорт")
        ]

        self.task_types = ["учёба", "спорт", "работа", "все"]
        self.filter_type = tk.StringVar(value="все")

        # Загружаем историю
        self.history = self.load_history()

        self.create_widgets()
        self.display_history()

    def create_widgets(self):
        # --- Генератор ---
        frame_gen = ttk.LabelFrame(self.root, text="🎲 Генератор случайной задачи", padding=10)
        frame_gen.pack(fill="x", padx=10, pady=5)

        ttk.Button(frame_gen, text="Сгенерировать задачу", command=self.generate_task).pack(pady=5)
        self.current_task_label = ttk.Label(frame_gen, text="", font=("Arial", 11, "bold"), foreground="green")
        self.current_task_label.pack()

        # --- Добавление своей задачи ---
        frame_add = ttk.LabelFrame(self.root, text="➕ Добавить новую задачу", padding=10)
        frame_add.pack(fill="x", padx=10, pady=5)

        ttk.Label(frame_add, text="Название:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.new_task_entry = ttk.Entry(frame_add, width=30)
        self.new_task_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame_add, text="Тип:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.new_type_combo = ttk.Combobox(frame_add, values=self.task_types[:-1], state="readonly", width=27)
        self.new_type_combo.current(0)
        self.new_type_combo.grid(row=1, column=1, padx=5, pady=5)

        ttk.Button(frame_add, text="Добавить", command=self.add_task).grid(row=2, column=0, columnspan=2, pady=10)

        # --- Фильтр ---
        frame_filter = ttk.LabelFrame(self.root, text="🔍 Фильтрация истории", padding=10)
        frame_filter.pack(fill="x", padx=10, pady=5)

        for t in self.task_types:
            rb = ttk.Radiobutton(frame_filter, text=t.capitalize(), variable=self.filter_type,
                                 value=t, command=self.display_history)
            rb.pack(side="left", padx=10)

        # --- История ---
        frame_history = ttk.LabelFrame(self.root, text="📜 История задач", padding=10)
        frame_history.pack(fill="both", expand=True, padx=10, pady=5)

        self.history_listbox = tk.Listbox(frame_history, height=12)
        scrollbar = ttk.Scrollbar(frame_history, orient="vertical", command=self.history_listbox.yview)
        self.history_listbox.configure(yscrollcommand=scrollbar.set)
        self.history_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # --- Кнопка сохранения ---
        ttk.Button(self.root, text="💾 Сохранить историю в JSON", command=self.save_history_to_json).pack(pady=5)

    def generate_task(self):
        task, task_type = random.choice(self.predefined_tasks)
        self.history.append({"task": task, "type": task_type})
        self.current_task_label.config(text=f"✅ {task} [{task_type}]")
        self.display_history()
        self.save_history_to_json()

    def add_task(self):
        task = self.new_task_entry.get().strip()
        task_type = self.new_type_combo.get()

        # Валидация
        if not task:
            messagebox.showerror("Ошибка ввода", "Название задачи не может быть пустым!")
            return

        self.predefined_tasks.append((task, task_type))
        self.history.append({"task": task, "type": task_type})

        self.new_task_entry.delete(0, tk.END)
        self.current_task_label.config(text=f"➕ Добавлено: {task} [{task_type}]")
        self.display_history()
        self.save_history_to_json()

    def display_history(self):
        self.history_listbox.delete(0, tk.END)
        current_filter = self.filter_type.get()

        for item in self.history:
            if current_filter == "все" or item["type"] == current_filter:
                self.history_listbox.insert(tk.END, f"{item['task']} — {item['type']}")

    def load_history(self):
        if not os.path.exists("tasks.json"):
            return []
        try:
            with open("tasks.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []

    def save_history_to_json(self):
        try:
            with open("tasks.json", "w", encoding="utf-8") as f:
                json.dump(self.history, f, indent=4, ensure_ascii=False)
        except IOError:
            messagebox.showerror("Ошибка", "Не удалось сохранить историю")


if __name__ == "__main__":
    root = tk.Tk()
    app = RandomTaskGenerator(root)
    root.mainloop()
  
