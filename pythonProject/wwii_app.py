import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import sqlite3
from datetime import datetime

class WWIIApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Учет погибших во Второй Мировой войне")
        self.root.geometry("1920x1000")
        self.root.configure(bg="#f0f0f0")

        # Подключение к БД
        self.conn = sqlite3.connect("wwii.db")
        self.cursor = self.conn.cursor()
        self.create_table()

        # Создание и настройка стилей
        self.create_styles()

        # Основной контейнер
        self.main_frame = ttk.Frame(root, style="Main.TFrame")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Заголовок
        self.title_label = ttk.Label(self.main_frame, text="Учёт погибших во Второй Мировой войне",
                                     style="Title.TLabel")
        self.title_label.pack(pady=(0, 20))

        # Фрейм для кнопок и таблицы
        self.content_frame = ttk.Frame(self.main_frame, style="Content.TFrame")
        self.content_frame.pack(fill=tk.BOTH, expand=True)

        # Кнопки
        self.button_frame = ttk.Frame(self.content_frame, style="Buttons.TFrame")
        self.button_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))

        buttons = [
            ("Добавить запись", self.open_add_record_window),
            ("Просмотр записей", self.view_records),
            ("Удалить запись", self.delete_record),
            ("Редактировать запись", self.edit_record),
            ("Фильтр", self.open_filter_window),

        ]

        for text, command in buttons:
            btn = ttk.Button(self.button_frame, text=text, command=command, style="Action.TButton")
            btn.pack(pady=10, padx=5, fill=tk.X)

        # Таблица для отображения данных с прокруткой
        self.tree_frame = ttk.Frame(self.content_frame, style="Tree.TFrame")
        self.tree_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.tree_scroll = ttk.Scrollbar(self.tree_frame)
        self.tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree = ttk.Treeview(self.tree_frame, columns=("ID", "Имя", "Фамилия", "Возраст", "Место смерти", "Дата смерти"),
                                 show='headings', yscrollcommand=self.tree_scroll.set, style="Custom.Treeview")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Имя", text="Имя")
        self.tree.heading("Фамилия", text="Фамилия")
        self.tree.heading("Возраст", text="Возраст")
        self.tree.heading("Место смерти", text="Место смерти")
        self.tree.heading("Дата смерти", text="Дата смерти")
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.tree_scroll.config(command=self.tree.yview)

        self.tree.bind("<ButtonRelease-1>", self.select_record)

        self.selected_record = None

    def delete_record(self):
        if self.selected_record:
            confirm = messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить эту запись?")
            if confirm:
                try:
                    self.cursor.execute("DELETE FROM dead_people WHERE id=?", (self.selected_record,))
                    self.conn.commit()
                    self.view_records()
                    self.selected_record = None
                    messagebox.showinfo("Успех", "Запись успешно удалена")
                except sqlite3.Error as e:
                    messagebox.showerror("Ошибка", f"Не удалось удалить запись: {e}")
        else:
            messagebox.showwarning("Предупреждение", "Выберите запись для удаления")
    def create_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        # Основной фрейм
        style.configure("Main.TFrame", background="#f0f0f0")

        # Заголовок
        style.configure("Title.TLabel", font=("Arial", 24, "bold"), background="#f0f0f0", foreground="#333333")

        # Контент
        style.configure("Content.TFrame", background="#ffffff")

        # Кнопки
        style.configure("Buttons.TFrame", background="#ffffff")
        style.configure("Action.TButton", font=("Arial", 12), padding=10)

        # Таблица
        style.configure("Tree.TFrame", background="#ffffff")
        style.configure("Custom.Treeview", background="#ffffff", fieldbackground="#ffffff", font=("Arial", 10))
        style.configure("Custom.Treeview.Heading", font=("Arial", 11, "bold"))

        # Стили для окон добавления/редактирования/фильтрации
        style.configure("Window.TFrame", background="#ffffff")
        style.configure("Window.TLabel", background="#ffffff", font=("Arial", 12))
        style.configure("Window.TEntry", font=("Arial", 12))
        style.configure("Window.TButton", font=("Arial", 12), padding=5)

    def create_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS dead_people (
                               id INTEGER PRIMARY KEY AUTOINCREMENT,
                               name TEXT,
                               surname TEXT,
                               age INTEGER,
                               place_of_death TEXT,
                               date_of_death TEXT)''')
        self.conn.commit()

    def open_add_record_window(self):
        add_window = tk.Toplevel(self.root)
        add_window.title("Добавить новую запись")
        add_window.geometry("400x300")
        add_window.configure(bg="#ffffff")

        frame = ttk.Frame(add_window, style="Window.TFrame")
        frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        fields = [("Имя:", "name"), ("Фамилия:", "surname"), ("Возраст:", "age"),
                  ("Место смерти:", "place"), ("Дата смерти (ДД.ММ.ГГГГ):", "date")]

        entries = {}
        for i, (label_text, field) in enumerate(fields):
            ttk.Label(frame, text=label_text, style="Window.TLabel").grid(row=i, column=0, padx=5, pady=5, sticky="e")
            entry = ttk.Entry(frame, style="Window.TEntry")
            entry.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
            entries[field] = entry

        entries["date"].bind("<KeyRelease>", self.format_date_entry)

        ttk.Button(frame, text="Сохранить", style="Window.TButton",
                   command=lambda: self.add_record(entries, add_window)).grid(row=len(fields), column=0, columnspan=2, pady=10)

        frame.grid_columnconfigure(1, weight=1)

    def add_record(self, entries, add_window):
        name = entries["name"].get()
        surname = entries["surname"].get()
        age = entries["age"].get()
        place_of_death = entries["place"].get()
        date_of_death = self.format_date_for_db(entries["date"].get())

        if name and surname and age and place_of_death and date_of_death:
            self.cursor.execute("INSERT INTO dead_people (name, surname, age, place_of_death, date_of_death) VALUES (?, ?, ?, ?, ?)",
                                (name, surname, age, place_of_death, date_of_death))
            self.conn.commit()
            self.view_records()
            add_window.destroy()
        else:
            messagebox.showwarning("Ошибка", "Все поля должны быть заполнены!")

    def view_records(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        self.cursor.execute("SELECT * FROM dead_people")
        records = self.cursor.fetchall()
        for record in records:
            # Преобразуем дату в формат ГГГГ-ММ-ДД для отображения
            record = list(record)
            record[5] = self.format_date_for_display(record[5])
            self.tree.insert('', 'end', values=record)

    def format_date_for_display(self, date_string):
        try:
            date_obj = datetime.strptime(date_string, "%Y-%m-%d")
            return date_obj.strftime("%Y-%m-%d")
        except ValueError:
            return date_string  # Возвращаем исходную строку, если не удалось преобразовать

    def edit_record(self):
        if self.selected_record:
            edit_window = tk.Toplevel(self.root)
            edit_window.title("Редактировать запись")
            edit_window.geometry("400x300")
            edit_window.configure(bg="#ffffff")

            frame = ttk.Frame(edit_window, style="Window.TFrame")
            frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

            self.cursor.execute("SELECT * FROM dead_people WHERE id=?", (self.selected_record,))
            record = self.cursor.fetchone()

            fields = [("Имя:", "name"), ("Фамилия:", "surname"), ("Возраст:", "age"),
                      ("Место смерти:", "place"), ("Дата смерти (ГГГГ-ММ-ДД):", "date")]

            entries = {}
            for i, (label_text, field) in enumerate(fields):
                ttk.Label(frame, text=label_text, style="Window.TLabel").grid(row=i, column=0, padx=5, pady=5, sticky="e")
                entry = ttk.Entry(frame, style="Window.TEntry")
                if i == 4:  # Поле даты
                    entry.insert(0, self.format_date_for_display(record[i+1]))
                else:
                    entry.insert(0, record[i+1])
                entry.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
                entries[field] = entry

            ttk.Button(frame, text="Сохранить", style="Window.TButton",
                       command=lambda: self.update_record(entries, edit_window)).grid(row=len(fields), column=0, columnspan=2, pady=10)

            frame.grid_columnconfigure(1, weight=1)
        else:
            messagebox.showwarning("Ошибка", "Выберите запись для редактирования.")

    def format_date_for_db(self, date_text):
        try:
            # Попробуем разные форматы даты
            for fmt in ("%d.%m.%Y", "%Y-%m-%d"):
                try:
                    date_obj = datetime.strptime(date_text, fmt)
                    return date_obj.strftime("%Y-%m-%d")
                except ValueError:
                    continue

            # Если ни один формат не подошел
            print(f"Некорректный формат даты: {date_text}")
            return None
        except Exception as e:
            print(f"Ошибка при обработке даты: {e}")
            return None

    def update_record(self, entries, edit_window):
        name = entries["name"].get().strip()
        surname = entries["surname"].get().strip()
        age = entries["age"].get().strip()
        place_of_death = entries["place"].get().strip()
        date_of_death = entries["date"].get().strip()

        # Отладочная информация
        print(f"Обновление записи:")
        print(f"ID: {self.selected_record}")
        print(f"Имя: '{name}'")
        print(f"Фамилия: '{surname}'")
        print(f"Возраст: '{age}'")
        print(f"Место смерти: '{place_of_death}'")
        print(f"Дата смерти: '{date_of_death}'")

        # Проверка заполненности полей
        if not all([name, surname, age, place_of_death, date_of_death]):
            messagebox.showwarning("Ошибка", "Все поля должны быть заполнены!")
            return

        # Проверка корректности возраста
        try:
            age = int(age)
            if age <= 0:
                raise ValueError("Возраст должен быть положительным числом")
        except ValueError as e:
            messagebox.showwarning("Ошибка", f"Некорректный возраст: {str(e)}")
            return

        # Проверка и форматирование даты
        try:
            date_obj = datetime.strptime(date_of_death, "%Y-%m-%d")
            formatted_date = date_obj.strftime("%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("Ошибка", f"Некорректный формат даты: {date_of_death}. Используйте ГГГГ-ММ-ДД")
            return

        # Обновление записи в базе данных
        try:
            self.cursor.execute(
                "UPDATE dead_people SET name=?, surname=?, age=?, place_of_death=?, date_of_death=? WHERE id=?",
                (name, surname, age, place_of_death, formatted_date, self.selected_record)
            )
            self.conn.commit()
            print("Запись успешно обновлена в базе данных")
            self.view_records()
            edit_window.destroy()
        except sqlite3.Error as e:
            print(f"Ошибка при обновлении записи в базе данных: {e}")
            messagebox.showerror("Ошибка", f"Не удалось обновить запись: {e}")


    def select_record(self, event):
        selected = self.tree.focus()
        values = self.tree.item(selected, 'values')
        if values:
            self.selected_record = values[0]
            print(f"Выбрана запись с ID: {self.selected_record}")  # Отладочная информация

    def format_date_entry(self, event):
        date_text = event.widget.get()

        if event.keysym == "BackSpace":
            if len(date_text) > 0 and (len(date_text) == 3 or len(date_text) == 6):
                event.widget.delete(len(date_text)-1, tk.END)
        elif len(date_text) == 2 or len(date_text) == 5:
            event.widget.insert(tk.END, '.')

    def format_date_for_db(self, date_text):
        try:
            # Преобразование даты из формата ДД.ММ.ГГГГ в ГГГГ-ММ-ДД
            day, month, year = date_text.split('.')
            return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        except ValueError:
            print(f"Invalid date format: {date_text}")
            return None

    def open_filter_window(self):
        filter_window = tk.Toplevel(self.root)
        filter_window.title("Фильтрация записей")
        filter_window.geometry("400x350")
        filter_window.configure(bg="#ffffff")

        frame = ttk.Frame(filter_window, style="Window.TFrame")
        frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        fields = [("Имя:", "name"), ("Фамилия:", "surname"), ("Возраст:", "age"),
                  ("Место смерти:", "place"), ("Дата смерти от (ДД.ММ.ГГГГ):", "start_date"),
                  ("Дата смерти до (ДД.ММ.ГГГГ):", "end_date")]

        entries = {}
        for i, (label_text, field) in enumerate(fields):
            ttk.Label(frame, text=label_text, style="Window.TLabel").grid(row=i, column=0, padx=5, pady=5, sticky="e")
            entry = ttk.Entry(frame, style="Window.TEntry")
            entry.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
            entries[field] = entry

        entries["start_date"].bind("<KeyRelease>", self.format_date_entry)
        entries["end_date"].bind("<KeyRelease>", self.format_date_entry)

        ttk.Button(frame, text="Фильтровать", style="Window.TButton",
                   command=lambda: self.filter_records(entries, filter_window)).grid(row=len(fields), column=0, columnspan=2, pady=10)

        frame.grid_columnconfigure(1, weight=1)

    def filter_records(self, entries, filter_window):
        query = "SELECT * FROM dead_people WHERE 1=1"
        params = []

        # Фильтрация по имени
        if entries["name"].get():
            query += " AND name LIKE ?"
            params.append(f"%{entries['name'].get()}%")

        # Фильтрация по фамилии
        if entries["surname"].get():
            query += " AND surname LIKE ?"
            params.append(f"%{entries['surname'].get()}%")

        # Фильтрация по возрасту
        if entries["age"].get():
            query += " AND age = ?"
            params.append(entries["age"].get())

        # Фильтрация по месту смерти
        if entries["place"].get():
            query += " AND place_of_death LIKE ?"
            params.append(f"%{entries['place'].get()}%")

        # Фильтрация по датам
        start_date = entries["start_date"].get()
        end_date = entries["end_date"].get()

        if start_date or end_date:
            if start_date:
                start_date = self.format_date_for_db(start_date)
                if start_date:
                    query += " AND date_of_death >= ?"
                    params.append(start_date)

            if end_date:
                end_date = self.format_date_for_db(end_date)
                if end_date:
                    query += " AND date_of_death <= ?"
                    params.append(end_date)

        # Отладочная информация
        print(f"SQL Query: {query}")
        print(f"Parameters: {params}")

        self.cursor.execute(query, params)
        records = self.cursor.fetchall()

        # Отладочная информация
        print(f"Number of records found: {len(records)}")

        for i in self.tree.get_children():
            self.tree.delete(i)
        for record in records:
            self.tree.insert('', 'end', values=record)

        filter_window.destroy()


    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = WWIIApp(root)
    root.mainloop()

