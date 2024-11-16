import psycopg2


def fill_wells_table():
    # Подключение к базе данных
    db_params = {
        'dbname': 'database',  # Замените на имя вашей базы данных
        'user': 'postgres',  # Замените на имя вашего пользователя
        'password': '147809qaZ',  # Замените на ваш пароль
        'host': 'localhost',  # Замените на ваш хост, если необходимо
        'port': '5432'  # Порт по умолчанию для PostgreSQL
    }

    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()


    # Заполнение таблицы wells данными из таблицы objects
    cursor.execute("""
            UPDATE wells
            SET 
                ngdu = FLOOR(well / 1000),
                cdng = FLOOR(well / 100),
                kust = FLOOR(well / 10),
                mest = well;
        """)

    # Сохранение изменений и закрытие соединения
    conn.commit()
    cursor.close()
    conn.close()
    print("Таблица wells успешно заполнена.")


def main():
    fill_wells_table()


if __name__ == "__main__":
    main()