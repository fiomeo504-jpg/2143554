import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json
import os

DATA_FILE = "expenses.json"
CATEGORIES = ["Еда", "Транспорт", "Развлечения", "Коммунальные услуги", 
              "Одежда", "Здоровье", "Косметика", "Образование", "Другое"]


class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker - Трекер расходов")
        self.root.geometry("950x680")
        self.root.resizable(True, True)

        self.expenses = []
        self.load_data()

        self.create_widgets()
        self.refresh_table()
        self.update_total_sum()

    def create_widgets(self):
        # === Рамка добавления расхода ===
        add_frame = tk.LabelFrame(self.root, text="➕ Добавить расход", padx=15, pady=10, font=("Arial", 10, "bold"))
        add_frame.pack(fill="x", padx=10, pady=5)

        # Сумма
        tk.Label(add_frame, text="Сумма (₽):", font=("Arial", 10)).grid(row=0, column=0, sticky="e", padx=5, pady=8)
        self.amount_entry = tk.Entry(add_frame, width=15, font=("Arial", 10))
        self.amount_entry.grid(row=0, column=1, padx=5, pady=8)

        # Категория
        tk.Label(add_frame, text="Категория:", font=("Arial", 10)).grid(row=0, column=2, sticky="e", padx=5, pady=8)
        self.category_var = tk.StringVar(value=CATEGORIES[0])
        self.category_combo = ttk.Combobox(add_frame, textvariable=self.category_var, 
                                            values=CATEGORIES, width=18, font=("Arial", 10))
        self.category_combo.grid(row=0, column=3, padx=5, pady=8)

        # Дата
        tk.Label(add_frame, text="Дата (ГГГГ-ММ-ДД):", font=("Arial", 10)).grid(row=0, column=4, sticky="e", padx=5, pady=8)
        self.date_entry = tk.Entry(add_frame, width=12, font=("Arial", 10))
        self.date_entry.grid(row=0, column=5, padx=5, pady=8)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        # Кнопка добавить
        tk.Button(add_frame, text="➕ Добавить расход", command=self.add_expense,
                  bg="lightgreen", font=("Arial", 10, "bold"), width=15).grid(row=0, column=6, padx=10, pady=8)

        # === Рамка фильтрации ===
        filter_frame = tk.LabelFrame(self.root, text="🔍 Фильтрация", padx=15, pady=10, font=("Arial", 10, "bold"))
        filter_frame.pack(fill="x", padx=10, pady=5)

        # Фильтр по категории
        tk.Label(filter_frame, text="Категория:", font=("Arial", 10)).grid(row=0, column=0, sticky="e", padx=5, pady=8)
        self.filter_category_var = tk.StringVar(value="Все")
        categories_filter = ["Все"] + CATEGORIES
        self.filter_category_combo = ttk.Combobox(filter_frame, textvariable=self.filter_category_var,
                                                   values=categories_filter, width=18, font=("Arial", 10))
        self.filter_category_combo.grid(row=0, column=1, padx=5, pady=8)

        # Фильтр по дате (диапазон)
        tk.Label(filter_frame, text="Дата от (ГГГГ-ММ-ДД):", font=("Arial", 10)).grid(row=0, column=2, sticky="e", padx=5, pady=8)
        self.filter_date_from = tk.Entry(filter_frame, width=12, font=("Arial", 10))
        self.filter_date_from.grid(row=0, column=3, padx=5, pady=8)

        tk.Label(filter_frame, text="до:", font=("Arial", 10)).grid(row=0, column=4, padx=2, pady=8)
        self.filter_date_to = tk.Entry(filter_frame, width=12, font=("Arial", 10))
        self.filter_date_to.grid(row=0, column=5, padx=5, pady=8)

        # Кнопки фильтрации
        tk.Button(filter_frame, text="🔍 Применить фильтр", command=self.apply_filter,
                  bg="lightblue", font=("Arial", 9)).grid(row=0, column=6, padx=5, pady=8)
        tk.Button(filter_frame, text="❌ Сбросить фильтр", command=self.reset_filter,
                  bg="lightgray", font=("Arial", 9)).grid(row=0, column=7, padx=5, pady=8)

        # === Рамка подсчёта суммы ===
        sum_frame = tk.LabelFrame(self.root, text="💰 Подсчёт расходов за период", padx=15, pady=10, font=("Arial", 10, "bold"))
        sum_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(sum_frame, text="Период от:", font=("Arial", 10)).grid(row=0, column=0, padx=5, pady=8)
        self.sum_date_from = tk.Entry(sum_frame, width=12, font=("Arial", 10))
        self.sum_date_from.grid(row=0, column=1, padx=5, pady=8)

        tk.Label(sum_frame, text="до:", font=("Arial", 10)).grid(row=0, column=2, padx=5, pady=8)
        self.sum_date_to = tk.Entry(sum_frame, width=12, font=("Arial", 10))
        self.sum_date_to.grid(row=0, column=3, padx=5, pady=8)

        tk.Button(sum_frame, text="💰 Рассчитать сумму", command=self.calculate_sum,
                  bg="lightyellow", font=("Arial", 10, "bold"), width=15).grid(row=0, column=4, padx=15, pady=8)

        self.sum_label = tk.Label(sum_frame, text="Общая сумма: 0.00 ₽", font=("Arial", 12, "bold"), fg="darkgreen")
        self.sum_label.grid(row=0, column=5, padx=20, pady=8)

        # === Таблица расходов ===
        table_frame = tk.LabelFrame(self.root, text="📋 Список расходов", padx=10, pady=10, font=("Arial", 10, "bold"))
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("ID", "Дата", "Категория", "Сумма (₽)")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)

        self.tree.heading("ID", text="ID")
        self.tree.heading("Дата", text="Дата")
        self.tree.heading("Категория", text="Категория")
        self.tree.heading("Сумма (₽)", text="Сумма (₽)")

        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("Дата", width=110, anchor="center")
        self.tree.column("Категория", width=150)
        self.tree.column("Сумма (₽)", width=100, anchor="e")

        scrollbar_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        self.tree.pack(side=tk.LEFT, fill="both", expand=True)
        scrollbar_y.pack(side=tk.RIGHT, fill="y")
        scrollbar_x.pack(side=tk.BOTTOM, fill="x")

        # === Кнопки управления ===
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(fill="x", padx=10, pady=10)

        tk.Button(btn_frame, text="💾 Сохранить в JSON", command=self.save_data,
                  bg="lightyellow", font=("Arial", 10), width=15).pack(side="left", padx=5)
        tk.Button(btn_frame, text="📂 Загрузить из JSON", command=self.load_data_interactive,
                  bg="lightyellow", font=("Arial", 10), width=15).pack(side="left", padx=5)
        tk.Button(btn_frame, text="🗑 Удалить выбранное", command=self.delete_selected,
                  bg="salmon", font=("Arial", 10), width=15).pack(side="left", padx=5)

        # Статистика
        self.stats_label = tk.Label(btn_frame, text="", font=("Arial", 9), fg="blue")
        self.stats_label.pack(side="right", padx=10)
        self.update_stats()

    def validate_date(self, date_str):
        if not date_str:
            return True
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def add_expense(self):
        amount_str = self.amount_entry.get().strip()
        category = self.category_var.get()
        date = self.date_entry.get().strip()

        # Валидация суммы
        try:
            amount = float(amount_str)
            if amount <= 0:
                messagebox.showerror("Ошибка", "Сумма должна быть положительным числом")
                return
        except ValueError:
            messagebox.showerror("Ошибка", "Сумма должна быть числом")
            return

        # Валидация даты
        if not self.validate_date(date):
            messagebox.showerror("Ошибка", "Дата должна быть в формате ГГГГ-ММ-ДД (например, 2026-04-30)")
            return

        # Генерация ID
        expense_id = len(self.expenses) + 1

        expense = {
            "id": expense_id,
            "date": date,
            "category": category,
            "amount": amount
        }

        self.expenses.append(expense)
        self.refresh_table()
        self.clear_inputs()
        self.update_stats()
        self.update_total_sum()
        messagebox.showinfo("Успех", f"Расход {amount:.2f} ₽ добавлен")

    def clear_inputs(self):
        self.amount_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.category_var.set(CATEGORIES[0])

    def refresh_table(self, expenses_to_show=None):
        for row in self.tree.get_children():
            self.tree.delete(row)

        data = expenses_to_show if expenses_to_show is not None else self.expenses
        for exp in data:
            self.tree.insert("", tk.END, values=(
                exp["id"],
                exp["date"],
                exp["category"],
                f"{exp['amount']:.2f}"
            ))

    def apply_filter(self):
        filtered = self.expenses[:]

        # Фильтр по категории
        category_filter = self.filter_category_var.get()
        if category_filter != "Все":
            filtered = [e for e in filtered if e["category"] == category_filter]

        # Фильтр по дате (диапазон)
        date_from = self.filter_date_from.get().strip()
        date_to = self.filter_date_to.get().strip()

        if date_from and not self.validate_date(date_from):
            messagebox.showerror("Ошибка", "Неверный формат даты 'от'")
            return
        if date_to and not self.validate_date(date_to):
            messagebox.showerror("Ошибка", "Неверный формат даты 'до'")
            return

        if date_from:
            filtered = [e for e in filtered if e["date"] >= date_from]
        if date_to:
            filtered = [e for e in filtered if e["date"] <= date_to]

        self.refresh_table(filtered)
        messagebox.showinfo("Фильтр", f"Показано расходов: {len(filtered)}")

    def reset_filter(self):
        self.filter_category_var.set("Все")
        self.filter_date_from.delete(0, tk.END)
        self.filter_date_to.delete(0, tk.END)
        self.refresh_table()
        self.update_total_sum()
        messagebox.showinfo("Фильтр", "Фильтр сброшен")

    def calculate_sum(self):
        date_from = self.sum_date_from.get().strip()
        date_to = self.sum_date_to.get().strip()

        if date_from and not self.validate_date(date_from):
            messagebox.showerror("Ошибка", "Неверный формат даты 'от'")
            return
        if date_to and not self.validate_date(date_to):
            messagebox.showerror("Ошибка", "Неверный формат даты 'до'")
            return

        total = 0
        for exp in self.expenses:
            if date_from and exp["date"] < date_from:
                continue
            if date_to and exp["date"] > date_to:
                continue
            total += exp["amount"]

        self.sum_label.config(text=f"Общая сумма: {total:.2f} ₽")
        messagebox.showinfo("Подсчёт", f"Сумма расходов за выбранный период: {total:.2f} ₽")

    def update_total_sum(self):
        total = sum(exp["amount"] for exp in self.expenses)
        self.sum_label.config(text=f"Общая сумма: {total:.2f} ₽ (всего)")

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите запись для удаления")
            return

        if messagebox.askyesno("Удаление", "Вы уверены, что хотите удалить выбранную запись?"):
            for item in selected:
                values = self.tree.item(item, "values")
                expense_id = int(values[0])
                # Удаляем по ID
                self.expenses = [e for e in self.expenses if e["id"] != expense_id]

            # Перенумеровываем ID
            for i, exp in enumerate(self.expenses):
                exp["id"] = i + 1

            self.refresh_table()
            self.update_stats()
            self.update_total_sum()
            messagebox.showinfo("Удаление", "Запись удалена")

    def update_stats(self):
        total_count = len(self.expenses)
        total_amount = sum(exp["amount"] for exp in self.expenses)
        self.stats_label.config(text=f"📊 Всего расходов: {total_count} | 💰 Общая сумма: {total_amount:.2f} ₽")

    def save_data(self):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.expenses, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Сохранение", f"Данные сохранены в {DATA_FILE}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить: {e}")

    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    self.expenses = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                self.expenses = []

    def load_data_interactive(self):
        self.load_data()
        self.refresh_table()
        self.update_stats()
        self.update_total_sum()
        messagebox.showinfo("Загрузка", f"Загружено расходов: {len(self.expenses)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()
  
