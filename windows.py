import sys
import psycopg2
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QComboBox, QTextEdit, QMessageBox, QLineEdit, QPushButton
)


class Database:
    """Класс для работы с базой данных пользователей."""
    def __init__(self):
        # Подключение к вашей базе данных PostgreSQL
        self.conn = psycopg2.connect(
            dbname='database',
            user='postgres',
            password='147809qaZ',
            host='localhost',  # или другой хост, если нужно
            port='5432'  # стандартный порт PostgreSQL
        )
        self.cursor = self.conn.cursor()
        # Убедимся, что таблица пользователей существует
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE,
                password VARCHAR(50)
            )
        ''')
        self.conn.commit()

    def register_user(self, username, password):
        """Регистрирует нового пользователя."""
        try:
            self.cursor.execute('INSERT INTO users (username, password) VALUES (%s, %s)', (username, password))
            self.conn.commit()
            return True
        except psycopg2.IntegrityError:
            self.conn.rollback()  # Откат при ошибке
            return False

    def authenticate_user(self, username, password):
        """Проверяет, существует ли пользователь с такими учетными данными."""
        self.cursor.execute('SELECT * FROM users WHERE username=%s AND password=%s', (username, password))
        return self.cursor.fetchone() is not None

    def get_object_names(self):
        """Возвращает список названий объектов из базы данных."""
        self.cursor.execute('SELECT name FROM objects')
        return [row[0] for row in self.cursor.fetchall()]


class LoginWindow(QWidget):
    """Окно авторизации."""

    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setWindowTitle("Авторизация")

        layout = QVBoxLayout()

        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText("Введите имя пользователя")
        layout.addWidget(QLabel("Имя пользователя:"))
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText("Введите пароль")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(QLabel("Пароль:"))
        layout.addWidget(self.password_input)

        self.login_button = QPushButton("Войти", self)
        self.login_button.clicked.connect(self.login_user)
        layout.addWidget(self.login_button)

        self.register_button = QPushButton("Зарегистрироваться", self)
        self.register_button.clicked.connect(self.open_registration)
        layout.addWidget(self.register_button)

        self.setLayout(layout)

    def login_user(self):
        """Обрабатывает вход пользователя."""
        username = self.username_input.text()
        password = self.password_input.text()

        if self.db.authenticate_user(username, password):
            self.main_window = MainWindow(self.db)
            self.main_window.show()
            self.close()  # Закрываем окно авторизации
        else:
            QMessageBox.warning(self, "Ошибка", "Неверное имя пользователя или пароль.")

    def open_registration(self):
        """Открывает окно регистрации."""
        self.registration_window = RegistrationWindow(self.db)
        self.registration_window.show()


class RegistrationWindow(QWidget):
    """Окно регистрации."""

    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setWindowTitle("Регистрация")

        layout = QVBoxLayout()

        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText("Введите имя пользователя")
        layout.addWidget(QLabel("Имя пользователя:"))
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText("Введите пароль")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(QLabel("Пароль:"))
        layout.addWidget(self.password_input)

        self.register_button = QPushButton("Зарегистрироваться", self)
        self.register_button.clicked.connect(self.register_user)
        layout.addWidget(self.register_button)

        self.setLayout(layout)

    def register_user(self):
        """Регистрирует нового пользователя."""
        username = self.username_input.text()
        password = self.password_input.text()

        if username and password:
            if self.db.register_user(username, password):
                QMessageBox.information(self, "Успех", "Пользователь зарегистрирован!")
                self.close()  # Закрываем окно регистрации
            else:
                QMessageBox.warning(self, "Ошибка", "Имя пользователя уже существует.")
        else:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, заполните все поля.")


class MainWindow(QWidget):
    """Основное окно приложения."""

    def __init__(self, db):
        super().__init__()
        self.db = db

        self.setWindowTitle("Скважины")

        # Основной вертикальный layout
        layout = QVBoxLayout()

        # Выпадающий список с запросами
        self.query_combo = QComboBox(self)
        self.query_combo.addItems([
            "Суточный дебит жидкости в м3",
            "Суточное электропотребление в КВт*ч",
            "Суточные затраты на содержание в у.е.",
            "Суточная наработка насоса в у.е."
        ])
        self.query_combo.setMaximumHeight(200)  # Ограничиваем высоту до 200 пикселей
        layout.addWidget(QLabel("Выберите запрос:"))
        layout.addWidget(self.query_combo)

        # Новый выпадающий список для объектов
        self.object_combo = QComboBox(self)
        object_names = self.db.get_object_names()
        self.object_combo.addItems(object_names)
        self.object_combo.setMaximumHeight(200)  # Ограничиваем высоту до 200 пикселей
        layout.addWidget(QLabel("Выберите объект:"))
        layout.addWidget(self.object_combo)

        # Текстовое поле для отображения результатов
        self.results_text = QTextEdit(self)
        self.results_text.setReadOnly(True)
        layout.addWidget(QLabel("Результаты:"))
        layout.addWidget(self.results_text)

        # Устанавливаем основной layout
        self.setLayout(layout)

        # Обработчик изменения выбранного элемента в выпадающем списке запросов и объектов
        self.query_combo.currentIndexChanged.connect(self.update_results)
        self.object_combo.currentIndexChanged.connect(self.update_results)

    def update_results(self):
        """Обновляет текстовое поле с результатами на основе выбранных запросов и объектов."""
        selected_query = self.query_combo.currentText()
        selected_object = self.object_combo.currentText()
        self.results_text.setPlainText(f"Выбранный запрос: {selected_query}\nВыбранный объект: {selected_object}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    db = Database()
    login_window = LoginWindow(db)
    login_window.resize(300, 200)
    login_window.show()
    sys.exit(app.exec())