import tkinter as tk
from tkinter import ttk, messagebox
import random
import json
import os

class RandomTaskGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Task Generator - Хисматуллина Снежана")
        self.root.geometry("600x550")
        self.root.resizable(True, True)

        # Предопределённые задачи
        self.predefined_tasks = [
            ("Прочитать статью по Python", "учёба"),
            ("Сделать 10 отжиманий", "спорт"),
            ("Написать отчёт по работе", "работа"),
            ("Выпить стакан воды", "спорт"),
            ("Посмотреть лекцию", "учёба"),
            ("Спланировать задачи на день", "работа"),
            ("Помыть посуду", "работа"),
            ("Пробежка 2 км", "спорт"),
            ("Решить 3 задачи на логику", "учёба")
        ]

        self.task_types = ["учёба", "спорт", "работа", "все"]
        self.filter_type = tk.StringVar(value="все")

        # Загружаем историю
        self.history = self.load_history()

        self.create_widgets()
        self.display_history()

    def create_widgets(self):
        # Рамка генератора
        frame_gen = ttk.LabelFrame(self.root, text="🎲 Генератор случайной задачи", padding=10)
        frame_gen.pack(fill="x", padx=10, pady=8)

        self.gen_button = ttk.Button(frame_gen, text="✨ Сгенерировать задачу", command=self.generate_task)
        self.gen_button.pack(pady=8)

        self.current_task_label = ttk.Label(frame_gen, text="", font=("Arial", 11, "bold"), foreground="green")
        self.current_task_label.pack()

        # Рамка добавления
        frame_add = ttk.LabelFrame(self.root, text="➕ Добавить новую задачу", padding=10)
        frame_add.pack(fill="x", padx=10, pady=8)

        ttk.Label(frame_add, text="Название задачи:").grid(row=0, column=0, padx=8, pady=8, sticky="e")
        self.new_task_entry = ttk.Entry(frame_add, width=32)
        self.new_task_entry.grid(row=0, column=1, padx=8, pady=8)

        ttk.Label(frame_add, text="Тип задачи:").grid(row=1, column=0, padx=8, pady=8, sticky="e")
        self.new_type_combo = ttk.Combobox(frame_add, values=self.task_types[:-1], state="readonly", width=29)
        self.new_type_combo.current(0)
        self.new_type_combo.grid(row=1, column=1, padx=8, pady=8)

        self.add_button = ttk.Button(frame_add, text="📌 Добавить", command=self.add_task)
        self.add_button.grid(row=2, column=0, columnspan=2, pady=12)

        # Рамка фильтрации
        frame_filter = ttk.LabelFrame(self.root, text="🔍 Фильтрация истории", padding=10)
        frame_filter.pack(fill="x", padx=10, pady=8)

        for t in self.task_types:
            rb = ttk.Radiobutton(frame_filter, text=t.capitalize(), variable=self.filter_type,
                                 value=t, command=self.display_history)
            rb.pack(side="left", padx=12)

        # Рамка истории
        frame_history = ttk.LabelFrame(self.root, text="📜 История задач", padding=10)
        frame_history.pack(fill="both", expand=True, padx=10, pady=8)

        self.history_listbox = tk.Listbox(frame_history, height=12, font=("Arial", 10))
        scrollbar = ttk.Scrollbar(frame_history, orient="vertical", command=self.history_listbox.yview)
        self.history_listbox.configure(yscrollcommand=scrollbar.set)
        self.history_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Кнопка сохранения
        self.save_button = ttk.Button(self.root, text="💾 Сохранить историю в JSON", command=self.save_history_to_json)
        self.save_button.pack(pady=10)

    def generate_task(self):
        task, task_type = random.choice(self.predefined_tasks)
        self.history.append({"task": task, "type": task_type})
        self.current_task_label.config(text=f"✅ {task} [{task_type}]")
        self.display_history()
        self.save_history_to_json()

    def add_task(self):
        task = self.new_task_entry.get().strip()
        task_type = self.new_type_combo.get()

        if not task:
            messagebox.showerror("Ошибка ввода", "❌ Название задачи не может быть пустым!")
            return

        self.predefined_tasks.append((task, task_type))
        self.history.append({"task": task, "type": task_type})

        self.new_task_entry.delete(0, tk.END)
        self.current_task_label.config(text=f"➕ Добавлено: {task} [{task_type}]")
        self.display_history()
        self.save_history_to_json()
        
        messagebox.showinfo("Успех", f"Задача '{task}' успешно добавлена!")

    def display_history(self):
        self.history_listbox.delete(0, tk.END)
        current_filter = self.filter_type.get()

        if not self.history:
            self.history_listbox.insert(tk.END, "📭 История пуста. Сгенерируйте или добавьте задачу.")
            return

        for item in self.history:
            if current_filter == "все" or item["type"] == current_filter:
                display_text = f"📌 {item['task']} — [{item['type']}]"
                self.history_listbox.insert(tk.END, display_text)

    def load_history(self):
        if not os.path.exists("tasks.json"):
            return []
        try:
            with open("tasks.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except (json.JSONDecodeError, IOError):
            return []

    def save_history_to_json(self):
        try:
            with open("tasks.json", "w", encoding="utf-8") as f:
                json.dump(self.history, f, indent=4, ensure_ascii=False)
        except IOError:
            messagebox.showerror("Ошибка", "❌ Не удалось сохранить историю в JSON!")


if __name__ == "__main__":
    root = tk.Tk()
    app = RandomTaskGenerator(root)
    root.mainloop()
    
