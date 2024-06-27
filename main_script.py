import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Publisher, Book, Shop, Stock, Sale
import urllib.parse

def get_publisher_sales(session, publisher_identifier):
    if publisher_identifier.isdigit():
        publisher_id = int(publisher_identifier)
        publishers = session.query(Publisher).filter(Publisher.id == publisher_id).all()
    else:
        publisher_name = f"%{publisher_identifier}%"
        publishers = session.query(Publisher).filter(Publisher.name.ilike(publisher_name)).all()

    if not publishers:
        print("Издатель не найден")
        return

    for publisher in publishers:
        print(f"Результаты для издателя: {publisher.name}")
        sales = (
            session.query(Book.title, Shop.name, Sale.price, Sale.date_sale)
            .select_from(Book)
            .join(Publisher, Book.id_publisher == Publisher.id)
            .join(Stock, Stock.id_book == Book.id)
            .join(Shop, Shop.id == Stock.id_shop)
            .join(Sale, Sale.id_stock == Stock.id)
            .filter(Publisher.id == publisher.id)
            .all()
        )

        for title, shop_name, price, date_sale in sales:
            print(f"{title} | {shop_name} | {price} | {date_sale}")

def main():
    user = os.getenv('DB_USER', 'myuser')
    password = os.getenv('DB_PASSWORD', 'mypassword')
    host = os.getenv('DB_HOST', 'localhost')
    dbname = os.getenv('DB_NAME', 'mydatabase')

    # Выводим значения переменных окружения для проверки
    print(f"user: {user}")
    print(f"password: {password}")
    print(f"host: {host}")
    print(f"dbname: {dbname}")

    try:
        # Кодируем параметры строки подключения
        user_encoded = urllib.parse.quote_plus(user)
        password_encoded = urllib.parse.quote_plus(password)
        host_encoded = urllib.parse.quote_plus(host)
        dbname_encoded = urllib.parse.quote_plus(dbname)

        DATABASE_URL = f"postgresql://{user_encoded}:{password_encoded}@{host_encoded}/{dbname_encoded}?client_encoding=utf8"

        print(f"DATABASE_URL: {DATABASE_URL}")

        engine = create_engine(DATABASE_URL, connect_args={"options": "-c timezone=utc"})
        print("Подключение к базе данных установлено успешно")

        # Пробуем выполнить простое подключение без создания таблиц
        connection = engine.connect()
        connection.close()
        print("Тестовое подключение выполнено успешно")
    except Exception as e:
        print(f"Ошибка подключения к базе данных: {e}")
        return

    try:
        Base.metadata.create_all(engine)
        print("Таблицы созданы успешно")
    except Exception as e:
        print(f"Ошибка при создании таблиц: {e}")
        return

    Session = sessionmaker(bind=engine)
    session = Session()

    publisher_identifier = input("Введите имя или идентификатор издателя: ")
    get_publisher_sales(session, publisher_identifier)

if __name__ == '__main__':
    main()
