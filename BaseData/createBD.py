import sqlalchemy as sq
import sqlalchemy.orm
import BaseData.models
import re
import json
import os


def get_info(info_puth):
    """Получение информации о Базе Данных и токена ТГ бота"""
    with open(info_puth, encoding='utf-8') as f:
        res = json.load(f)                                          # Извлечение информации из файла
        return (res['postgreSQL']['bd'],
                res['postgreSQL']['login'],
                res['postgreSQL']['password'],
                res['postgreSQL']['name_bd'],
                res['postgreSQL']['create'],
                res['token_bot'])

def create_engine(info_puth):
    '''Функция для создания движка подключения к БД'''
    bd = get_info(info_puth)                                        # Получение информации о Базе Данных
    puthBD = f"{bd[0]}://{bd[1]}:{bd[2]}@localhost:5432/{bd[3]}"    # Создание пути для Базы данных
    return sq.create_engine(puthBD)

def create_bd(info_puth):
    '''Функция для создания базы данных'''
    engine = create_engine(info_puth)                               # Получение движка
    session = sqlalchemy.orm.sessionmaker(engine)()                 # Подключение к сессии
    BaseData.models.basic.metadata.drop_all(engine)                 # Удаление таблиц с таким же именем, если они есть
    BaseData.models.basic.metadata.create_all(engine)               # Создание таблиц
    print('БД успешна создана')
    session.commit(), session.close()                               # Коммит и закрытие сессии

    # --- После создания Базы данных изменить статус create на True, чтобы БД не пересоздавалась в будущем ---
    info_bd = get_info(info_puth)
    with open(info_puth, 'w', encoding='utf-8') as f:
        json.dump({'postgreSQL':
                       {'bd': info_bd[0],
                        'login': info_bd[1],
                        'password': info_bd[2],
                        'name_bd': info_bd[3],
                        'create': True},
                   'token_bot': info_bd[5]}, f, indent=5)

def loads_words(info_puth, name_file='words.txt'):
    '''Функция загружает слова в базу данных'''
    engine = create_engine(info_puth)                                                   # Получение движка
    session = sqlalchemy.orm.sessionmaker(engine)()                                     # Подключение к сессии

    # --- Обработка файла и загрузка в Базу Данных ---
    path = os.path.join(os.getcwd(), os.path.join('BaseData', name_file))               # Путь до файла со словами
    with open(path, encoding='utf-8') as f:
        reader = f.readlines()
        for i, el in enumerate(reader, 1):
            eng = el.split()[0]                                                         # Слово на английском
            ru = re.findall(r'\]\s+([\w ,\(\)-\.\!\/]+)\s+Войти', el)[0]                # Слово на русском
            trz = el.split()[1]                                                         # Транскрипция
            session.add(BaseData.models.AllWords(eng_word=eng, ru_word=ru, tr=trz))     # Загрузка в бд
        session.commit(), session.close()                                               # Коммит и закрытие сессии


