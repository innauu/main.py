import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import json
import os

class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")
        self.root.geometry("900x600")
        self.root.resizable(True, True)
        
        # Файл для хранения данных
        self.data_file = "expenses.json"
        
        # Загрузка данных
        self.expenses = self.load_data()
        
        # Создание интерфейса
        self.create_widgets()
        
        # Обновление таблицы
        self.refresh_table()
        self.update_total()
    
    def create_widgets(self):
        # Главный контейнер
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Настройка весов для растягивания
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(5, weight=1)
        
        # Фрейм для ввода данных
        input_frame = ttk.LabelFrame(main_frame, text="Добавление расхода", padding="10")
        input_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Сумма
        ttk.Label(input_frame, text="Сумма:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.amount_var = tk.StringVar()
        self.amount_entry = ttk.Entry(input_frame, textvariable=self.amount_var, width=15)
        self.amount_entry.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        
        # Категория
        ttk.Label(input_frame, text="Категория:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(input_frame, textvariable=self.category_var, 
                                          values=["еда", "транспорт", "развлечения", "здоровье", 
                                                 "образование", "одежда", "коммунальные услуги", "другое"],
                                          width=20, state="readonly")
        self.category_combo.grid(row=0, column=3, sticky=tk.W, padx=(0, 20))
        self.category_combo.set("еда")
        
        # Дата
        ttk.Label(input_frame, text="Дата (ДД.ММ.ГГГГ):").grid(row=0, column=4, sticky=tk.W, padx=(0, 5))
        self.date_var = tk.StringVar(value=datetime.now().strftime("%d.%m.%Y"))
        self.date_entry = ttk.Entry(input_frame, textvariable=self.date_var, width=12)
        self.date_entry.grid(row=0, column=5, sticky=tk.W, padx=(0, 10))
        
        # Кнопка добавления
        self.add_button = ttk.Button(input_frame, text="Добавить расход", command=self.add_expense)
        self.add_button.grid(row=0, column=6, padx=(10, 0))
        
        # Фрейм для фильтрации
        filter_frame = ttk.LabelFrame(main_frame, text="Фильтрация", padding="10")
        filter_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Фильтр по категории
        ttk.Label(filter_frame, text="По категории:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.filter_category_var = tk.StringVar(value="все")
        self.filter_category_combo = ttk.Combobox(filter_frame, textvariable=self.filter_category_var,
                                                 values=["все", "еда", "транспорт", "развлечения", 
                                                        "здоровье", "образование", "одежда", 
                                                        "коммунальные услуги", "другое"],
                                                 width=20, state="readonly")
        self.filter_category_combo.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        self.filter_category_combo.bind('<<ComboboxSelected>>', lambda e: self.apply_filters())
        
        # Фильтр по дате
        ttk.Label(filter_frame, text="С:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.filter_date_from_var = tk.StringVar()
        self.filter_date_from = ttk.Entry(filter_frame, textvariable=self.filter_date_from_var, width=12)
        self.filter_date_from.grid(row=0, column=3, sticky=tk.W, padx=(0, 10))
        
        ttk.Label(filter_frame, text="По:").grid(row=0, column=4, sticky=tk.W, padx=(0, 5))
        self.filter_date_to_var = tk.StringVar()
        self.filter_date_to = ttk.Entry(filter_frame, textvariable=self.filter_date_to_var, width=12)
        self.filter_date_to.grid(row=0, column=5, sticky=tk.W, padx=(0, 10))
        
        # Кнопки фильтрации
        self.apply_filter_button = ttk.Button(filter_frame, text="Применить фильтр", 
                                             command=self.apply_filters)
        self.apply_filter_button.grid(row=0, column=6, padx=(0, 5))
        
        self.clear_filter_button = ttk.Button(filter_frame, text="Сбросить фильтры", 
                                             command=self.clear_filters)
        self.clear_filter_button.grid(row=0, column=7)
        
        # Фрейм для итоговой суммы
        total_frame = ttk.LabelFrame(main_frame, text="Итоговая сумма", padding="10")
        total_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.total_label = ttk.Label(total_frame, text="Общая сумма расходов: 0.00 ₽", 
                                    font=("Arial", 12, "bold"))
        self.total_label.pack()
        
        # Таблица расходов
        table_frame = ttk.LabelFrame(main_frame, text="Список расходов", padding="10")
        table_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        
        # Создание Treeview
        columns = ("id", "amount", "category", "date")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        # Определение заголовков
        self.tree.heading("id", text="ID")
        self.tree.heading("amount", text="Сумма")
        self.tree.heading("category", text="Категория")
        self.tree.heading("date", text="Дата")
        
        # Настройка ширины колонок
        self.tree.column("id", width=50)
        self.tree.column("amount", width=100)
        self.tree.column("category", width=150)
        self.tree.column("date", width=100)
        
        # Добавление скроллбара
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Размещение таблицы и скроллбара
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Кнопка удаления
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        self.delete_button = ttk.Button(button_frame, text="Удалить выбранный расход", 
                                       command=self.delete_expense)
        self.delete_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.save_button = ttk.Button(button_frame, text="Сохранить данные", 
                                     command=self.save_data)
        self.save_button.pack(side=tk.LEFT)
    
    def validate_input(self):
        """Проверка корректности ввода данных"""
        # Проверка суммы
        try:
            amount = float(self.amount_var.get().replace(',', '.'))
            if amount <= 0:
                messagebox.showerror("Ошибка", "Сумма должна быть положительным числом!")
                return False
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректную сумму (число)!")
            return False
        
        # Проверка даты
        date_str = self.date_var.get().strip()
        try:
            datetime.strptime(date_str, "%d.%m.%Y")
        except ValueError:
            messagebox.showerror("Ошибка", "Введите дату в формате ДД.ММ.ГГГГ!")
            return False
        
        # Проверка категории
        if not self.category_var.get():
            messagebox.showerror("Ошибка", "Выберите категорию!")
            return False
        
        return True
    
    def add_expense(self):
        """Добавление нового расхода"""
        if not self.validate_input():
            return
        
        amount = float(self.amount_var.get().replace(',', '.'))
        category = self.category_var.get()
        date = self.date_var.get().strip()
        
        # Создание записи
        expense = {
            "amount": amount,
            "category": category,
            "date": date
        }
        
        self.expenses.append(expense)
        
        # Очистка полей
        self.amount_var.set("")
        self.category_var.set("еда")
        self.date_var.set(datetime.now().strftime("%d.%m.%Y"))
        
        # Сохранение и обновление
        self.save_data()
        self.refresh_table()
        self.update_total()
        
        messagebox.showinfo("Успех", "Расход успешно добавлен!")
    
    def delete_expense(self):
        """Удаление выбранного расхода"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите расход для удаления!")
            return
        
        # Получаем ID выбранного элемента
        item = self.tree.item(selected[0])
        expense_id = item['values'][0]
        
        # Удаляем из списка
        if 0 <= expense_id < len(self.expenses):
            del self.expenses[expense_id]
            
            # Сохранение и обновление
            self.save_data()
            self.refresh_table()
            self.update_total()
            
            messagebox.showinfo("Успех", "Расход успешно удален!")
    
    def apply_filters(self):
        """Применение фильтров"""
        self.refresh_table()
        self.update_total()
    
    def clear_filters(self):
        """Сброс фильтров"""
        self.filter_category_var.set("все")
        self.filter_date_from_var.set("")
        self.filter_date_to_var.set("")
        self.refresh_table()
        self.update_total()
    
    def get_filtered_expenses(self):
        """Получение отфильтрованного списка расходов"""
        filtered = self.expenses.copy()
        
        # Фильтр по категории
        if self.filter_category_var.get() != "все":
            filtered = [e for e in filtered if e["category"] == self.filter_category_var.get()]
        
        # Фильтр по дате
        date_from = self.filter_date_from_var.get().strip()
        date_to = self.filter_date_to_var.get().strip()
        
        if date_from:
            try:
                from_date = datetime.strptime(date_from, "%d.%m.%Y")
                filtered = [e for e in filtered 
                           if datetime.strptime(e["date"], "%d.%m.%Y") >= from_date]
            except ValueError:
                pass
        
        if date_to:
            try:
                to_date = datetime.strptime(date_to, "%d.%m.%Y")
                filtered = [e for e in filtered 
                           if datetime.strptime(e["date"], "%d.%m.%Y") <= to_date]
            except ValueError:
                pass
        
        return filtered
    
    def refresh_table(self):
        """Обновление таблицы"""
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Заполнение данными
        filtered = self.get_filtered_expenses()
        for i, expense in enumerate(filtered):
            self.tree.insert("", tk.END, values=(
                i,
                f"{expense['amount']:.2f}",
                expense['category'],
                expense['date']
            ))
    
    def update_total(self):
        """Обновление общей суммы"""
        filtered = self.get_filtered_expenses()
        total = sum(expense['amount'] for expense in filtered)
        self.total_label.config(text=f"Общая сумма расходов: {total:.2f} ₽")
    
    def save_data(self):
        """Сохранение данных в JSON файл"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.expenses, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при сохранении данных: {str(e)}")
    
    def load_data(self):
        """Загрузка данных из JSON файла"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при загрузке данных: {str(e)}")
                return []
        return []

def main():
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()

if __name__ == "__main__":
    main()
