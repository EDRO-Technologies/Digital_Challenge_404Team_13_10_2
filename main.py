import psycopg2

# Подключение к базе данных

db_params = {
    'dbname': 'database',  # Замените на имя вашей базы данных
    'user': 'postgres',  # Замените на имя вашего пользователя
    'password': '147809qaZ',  # Замените на ваш пароль
    'host': 'localhost',  # Замените на ваш хост, если необходимо
    'port': '5432'  # Порт по умолчанию для PostgreSQL
}

conn = psycopg2.connect(**db_params)
cur = conn.cursor()

# Открываем файл и читаем его построчно
with open('/home/pc/Downloads/fact.txt', 'r', encoding='utf-8') as file:
    for line in file:
        line = line.strip()
        if line:  # Проверяем, что строка не пустая
            try:
                cur.execute(line)  # Выполняем команду INSERT
                conn.commit()  # Подтверждаем изменения
            except Exception as e:
                print(f"Ошибка при выполнении запроса: {line}")
                print(e)
                conn.rollback()  # Откатываем изменения, если произошла ошибка

# Закрываем соединение
cur.close()
conn.close()


# CREATE TABLE objects_type (
#   id SERIAL PRIMARY KEY,
#   name VARCHAR(42)
# );
#
# CREATE TABLE objects (
#   id SERIAL PRIMARY KEY,
#   name VARCHAR(42),
#   type INTEGER REFERENCES objects_type(id)
# );
#
# CREATE TABLE wells (
#   well INTEGER PRIMARY KEY,
#   ngdu INTEGER,
#   cdng INTEGER,
#   kust INTEGER,
#   mest INTEGER
# );
#
# CREATE TABLE well_day_histories (
#   well INTEGER REFERENCES wells(well),
#   date_fact DATE,
#   debit FLOAT,
#   ee_consume FLOAT,
#   expenses FLOAT,
#   pump_operating FLOAT
# );
#
# CREATE TABLE well_day_plans (
#   well INTEGER REFERENCES wells(well),
#   date_plan DATE,
#   debit FLOAT,
#   ee_consume FLOAT,
#   expenses FLOAT,
#   pump_operating FLOAT
# );

