import psycopg2

# Функция для обновления значения mest в таблице wells
def update_well_mest(cdng, new_mest):
    try:
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

        # SQL-запрос для обновления значения mest
        update_query = """
        UPDATE wells
        SET mest = %s
        WHERE cdng = %s;
        """

        # Выполнение обновления
        cursor.execute(update_query, (new_mest, cdng))
        conn.commit()

        print("Данные успешно обновлены.")

    except (Exception, psycopg2.DatabaseError) as error:
        print("Ошибка при обновлении данных:", error)

    finally:
        # Закрытие курсора и соединения
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Получение пользовательского ввода
cdng_input = input("Введите значение cdng: ")
new_mest_input = input("Введите новое значение mest: ")

# Вызов функции обновления
update_well_mest(cdng_input, new_mest_input)