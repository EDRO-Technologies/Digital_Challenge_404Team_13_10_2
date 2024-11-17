import sys
from time import perf_counter

import psycopg2
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QComboBox, QTextEdit, QMessageBox, QLineEdit, QPushButton
)
from PyQt6.QtWidgets import QDateEdit
from PyQt6.QtCore import QDate
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class Database:
    """Класс для работы с базой данных пользователей."""

    def __init__(self):
        self.conn = psycopg2.connect(
            dbname='database',
            user='postgres',
            password='147809qaZ',
            host='localhost',
            port='5432'
        )
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE,
                password VARCHAR(50)
            )
        ''')
        self.conn.commit()

    def register_user(self, username, password):
        try:
            self.cursor.execute('INSERT INTO users (username, password) VALUES (%s, %s)', (username, password))
            self.conn.commit()
            return True
        except psycopg2.IntegrityError:
            self.conn.rollback()
            return False

    def authenticate_user(self, username, password):
        self.cursor.execute('SELECT * FROM users WHERE username=%s AND password=%s', (username, password))
        return self.cursor.fetchone() is not None

    def get_object_names(self):
        self.cursor.execute('SELECT name FROM objects')
        return [row[0] for row in self.cursor.fetchall()]

    def get_data(self, query_type, name_date, start_date, end_date, schema='well_day_histories'):
        """Получает данные из указанной таблицы в зависимости от типа запроса."""
        column_map = {
            "Суточный дебит жидкости в м3": "debit",
            "Суточное электропотребление в КВт*ч": "ee_consume",
            "Суточные затраты на содержание в у.е.": "expenses",
            "Суточная наработка насоса в у.е.": "pump_operating"
        }

        column = column_map.get(query_type)
        print(name_date)
        self.cursor.execute('SELECT id, type FROM objects WHERE name = %s', (name_date,))
        id1, type = self.cursor.fetchone()
        # type = self.cursor.execute('SELECT type FROM objects WHERE name=%s', (name_date,))
        # id1 = self.cursor.execute('SELECT id FROM objects WHERE name=%s', (name_date,))
        well = 1111
        if type == int('5'):
            self.cursor.execute('SELECT well FROM wells WHERE mest=%s', (id1,))
            well = self.cursor.fetchone()
        elif type == int('1'):
            self.cursor.execute('SELECT well FROM wells WHERE ngdu=%s', (id1,))
            well = self.cursor.fetchone()
        elif type == int('2'):
            self.cursor.execute('SELECT well FROM wells WHERE cdng=%s', (id1,))
            well = self.cursor.fetchone()
        elif type == int('3'):
            self.cursor.execute('SELECT well FROM wells WHERE kust=%s', (id1,))
            well = self.cursor.fetchone()
        elif type == int('4'):
            self.cursor.execute('SELECT well FROM wells WHERE well=%s', (id1,))
            well = self.cursor.fetchone()
        print(well)
        if schema == 'well_day_histories':
            data = 'date_fact'
        else:
            data = 'date_plan'
        if column:
            self.cursor.execute(f'''
                SELECT {data}, {column} FROM {schema} WHERE well=%s
                AND {data} BETWEEN %s AND %s
                ORDER BY {data}
            ''', (well, start_date, end_date))
            return self.cursor.fetchall()
        return []


class LoginWindow(QWidget):
    """Окно авторизации."""

    def __init__(self, parent=None, db=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("Авторизация")
        layout = QVBoxLayout()

        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText("Имя пользователя")
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText("Пароль")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input)

        self.login_button = QPushButton("Войти", self)
        self.login_button.clicked.connect(self.login)
        layout.addWidget(self.login_button)

        self.register_button = QPushButton("Регистрация", self)
        self.register_button.clicked.connect(self.open_registration)
        layout.addWidget(self.register_button)

        self.setLayout(layout)

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        if self.db.authenticate_user(username, password):
            self.main_window = MainWindow(self.db)
            self.main_window.resize(800, 600)
            self.main_window.show()
            self.close()  # Закрываем текущее окно
        else:
            QMessageBox.warning(self, "Ошибка", "Неверные имя пользователя или пароль.")

    def open_registration(self):
        self.registration_window = RegistrationWindow(self.db)
        self.registration_window.resize(300, 200)
        self.registration_window.show()


class RegistrationWindow(QWidget):
    """Окно регистрации."""

    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setWindowTitle("Регистрация")
        layout = QVBoxLayout()

        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText("Имя пользователя")
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText("Пароль")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input)

        self.register_button = QPushButton("Зарегистрироваться", self)
        self.register_button.clicked.connect(self.register)
        layout.addWidget(self.register_button)

        self.setLayout(layout)

    def register(self):
        username = self.username_input.text()
        password = self.password_input.text()
        if self.db.register_user(username, password):
            QMessageBox.information(self, "Успех", "Пользователь зарегистрирован!")
            self.close()
        else:
            QMessageBox.warning(self, "Ошибка", "Пользователь с таким именем уже существует.")


class MainWindow(QWidget):
    """Основное окно приложения."""

    def __init__(self, db):
        super().__init__()
        self.db = db

        self.setWindowTitle("Скважины")
        layout = QVBoxLayout()

        self.query_combo = QComboBox(self)
        self.query_combo.addItems([
            "Суточный дебит жидкости в м3",
            "Суточное электропотребление в КВт*ч",
            "Суточные затраты на содержание в у.е.",
            "Суточная наработка насоса в у.е."
        ])
        layout.addWidget(QLabel("Выберите запрос:"))
        layout.addWidget(self.query_combo)

        self.object_combo = QComboBox(self)
        object_names = self.db.get_object_names()
        self.object_combo.addItems(object_names)
        layout.addWidget(QLabel("Выберите объект:"))
        layout.addWidget(self.object_combo)

        self.start_date_edit = QDateEdit(self)
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDate(QDate.currentDate())
        layout.addWidget(QLabel("Выберите начальную дату:"))
        layout.addWidget(self.start_date_edit)

        self.end_date_edit = QDateEdit(self)
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDate(QDate.currentDate())
        layout.addWidget(QLabel("Выберите конечную дату:"))
        layout.addWidget(self.end_date_edit)

        self.results_text = QTextEdit(self)
        self.results_text.setReadOnly(True)
        layout.addWidget(QLabel("Результаты:"))
        layout.addWidget(self.results_text)

        # Добавляем область для графика
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        self.setLayout(layout)

        self.query_combo.currentIndexChanged.connect(self.update_results)
        self.object_combo.currentIndexChanged.connect(self.update_results)
        self.start_date_edit.dateChanged.connect(self.update_results)
        self.end_date_edit.dateChanged.connect(self.update_results)

    def update_results(self):
        """Обновляет текстовое поле с результатами и график."""
        selected_query = self.query_combo.currentText()
        selected_object = self.object_combo.currentText()
        start_date = self.start_date_edit.date().toString("yyyy-MM-dd")
        end_date = self.end_date_edit.date().toString("yyyy-MM-dd")

        # Получаем данные из базы данных для well_day_histories
        data_fact = self.db.get_data(selected_query, selected_object, start_date, end_date, schema='well_day_histories')

        # Получаем данные из базы данных для well_day_plans
        data_plan = self.db.get_data(selected_query, selected_object, start_date, end_date, schema='well_day_plans')

        # Обновляем текстовое поле
        self.results_text.setPlainText(f"Выбранный запрос: {selected_query}\n"
                                       f"Выбранный объект: {selected_object}\n"
                                       f"Начальная дата: {start_date}\n"
                                       f"Конечная дата: {end_date}")

        # Обновляем график
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        # Отображаем данные из well_day_histories (синий график)
        if data_fact:
            dates_fact, values_fact = zip(*data_fact)  # Распаковываем даты и значения
            ax.plot(dates_fact, values_fact, marker='o', color='blue', label='well_day_histories')

        # Отображаем данные из well_day_plans (красный график)
        if data_plan:
            dates_plan, values_plan = zip(*data_plan)  # Распаковываем даты и значения
            ax.plot(dates_plan, values_plan, marker='o', color='red', label='well_day_plans')

        ax.set_title(selected_query)
        ax.set_xlabel('Дата')
        ax.set_ylabel(selected_query)
        ax.grid()
        ax.legend()  # Добавляем легенду
        self.canvas.draw()  # Обновляем график


def main():
    app = QApplication(sys.argv)

    try:
        db = Database()
        login_window = LoginWindow(None, db)  # Передаем None как родителя
        login_window.resize(300, 200)
        login_window.show()
        sys.exit(app.exec())
    except Exception as e:
        print(f"Ошибка подключения к базе данных: {e}")


if __name__ == "__main__":
    main()
