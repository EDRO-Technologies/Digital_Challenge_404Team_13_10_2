import sys
import psycopg2
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QComboBox, QTextEdit, QDateEdit
from PyQt6.QtCore import QDate


class Database:
    """Класс для работы с базой данных PostgreSQL."""

    def __init__(self, dbname, user, password, host, port):
        self.conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        self.cursor = self.conn.cursor()

    def get_object_names(self):
        """Получает имена объектов из базы данных."""
        self.cursor.execute("SELECT name FROM objects")  # Измените на вашу таблицу и колонку
        rows = self.cursor.fetchall()
        return [row[0] for row in rows]

    def close(self):
        """Закрывает соединение с базой данных."""
        self.cursor.close()
        self.conn.close()


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

        # Календарь для выбора диапазона дат
        self.start_date_edit = QDateEdit(self)
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDate(QDate.currentDate())  # Устанавливаем текущую дату по умолчанию
        layout.addWidget(QLabel("Выберите начальную дату:"))
        layout.addWidget(self.start_date_edit)

        self.end_date_edit = QDateEdit(self)
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDate(QDate.currentDate())  # Устанавливаем текущую дату по умолчанию
        layout.addWidget(QLabel("Выберите конечную дату:"))
        layout.addWidget(self.end_date_edit)

        # Текстовое поле для отображения результатов
        self.results_text = QTextEdit(self)
        self.results_text.setReadOnly(True)
        layout.addWidget(QLabel("Результаты:"))
        layout.addWidget(self.results_text)

        # Устанавливаем основной layout
        self.setLayout(layout)

        # Обработчик изменения выбранного элемента в выпадающих списках и датах
        self.query_combo.currentIndexChanged.connect(self.update_results)
        self.object_combo.currentIndexChanged.connect(self.update_results)
        self.start_date_edit.dateChanged.connect(self.update_results)
        self.end_date_edit.dateChanged.connect(self.update_results)

    def update_results(self):
        """Обновляет текстовое поле с результатами на основе выбранных запросов, объектов и дат."""
        selected_query = self.query_combo.currentText()
        selected_object = self.object_combo.currentText()
        start_date = self.start_date_edit.date().toString("yyyy-MM-dd")
        end_date = self.end_date_edit.date().toString("yyyy-MM-dd")

        # Здесь вы можете добавить логику для выполнения запроса к базе данных
        # в зависимости от выбранного запроса и объекта.

        # Пример: просто выводим выбранные значения
        self.results_text.setPlainText(f"Выбранный запрос: {selected_query}\n"
                                       f"Выбранный объект: {selected_object}\n"
                                       f"Начальная дата: {start_date}\n"
                                       f"Конечная дата: {end_date}")


def main():
    app = QApplication(sys.argv)

    # Замените эти параметры на свои данные для подключения к базе данных
    dbname = "database"  # Имя вашей базы данных
    user = "postgres"    # Ваше имя пользователя
    password = "147809qaZ" # Ваш пароль
    host = "localhost"         # Хост, на котором работает PostgreSQL
    port = "5432"              # Порт, на котором работает PostgreSQL

    try:
        db = Database(dbname, user, password, host, port)  # Создаем экземпляр базы данных
        window = MainWindow(db)
        window.show()

        # Закрываем соединение при завершении приложения
        app.aboutToQuit.connect(db.close)

        sys.exit(app.exec())
    except Exception as e:
        print(f"Ошибка подключения к базе данных: {e}")

if __name__ == "__main__":
    main()