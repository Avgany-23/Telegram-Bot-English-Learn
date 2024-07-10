from BaseData.models import *
from BaseData.createBD import *
import os
import random
import sqlalchemy as sq
import sqlalchemy.orm




class FuncBD():
    def __init__(self):
        '''Путь к Базе Данных'''
        bd = get_info(os.path.join(os.getcwd(), 'info.json'))
        self.puthBD = f"{bd[0]}://{bd[1]}:{bd[2]}@localhost:5432/{bd[3]}"
        self.engine = sq.create_engine(self.puthBD)
        self.session = sqlalchemy.orm.sessionmaker(self.engine)()


    def info_user(self, id_user):
        '''Получение информации о пользователе'''
        users = [(i.id_tg, i.first_name, i.username, i.yandex_token)
                 for i in self.session.query(Users).filter(Users.id_tg == id_user)]
        return users


    def info_user_language(self, id_user):
        "Получение информации о установленном пользователе языке"
        language = self.session.query(TranslatorWord).filter(TranslatorWord.id_user == id_user)
        return [i.language for i in language]


    def full_info_user(self, id_user):
        """Получение полной информации о пользователе"""
        basic_info = FuncBD().info_user(id_user)                        # Вся информация из таблицы Users в БД
        lang = FuncBD().info_user_language(id_user)                     # Информация о выбранном языке перевода
        words_dict = FuncBD().user_count_words(id_user, 'dict')         # Информация о добавленных слов в словарь
        words_favorite = FuncBD().user_count_words(id_user, 'favorite') # Информация о добавленных слов в избранное
        notif_user = FuncBD().notif_users(id_user, all_users=False)     # Информация об уведомлениях пользователя
        statistics_words = FuncBD().show_result_user(id_user)           # Информация и проценте правильных выбранных слов
        if statistics_words is None:
            statistics_words = 'нет информации'
        elif statistics_words == 0:
            statistics_words = '0 %'
        else:
            statistics_words = f"{statistics_words * 100}%"
        if not lang:
            lang = ['не установлен']
        return basic_info, lang, words_dict, words_favorite, statistics_words, notif_user


    def add_user(self, id, first_name, last_name):
        '''Добавление id пользователя в БД'''
        users = self.session.query(Users)
        id_user = [el.id_tg for el in users]
        if id not in id_user:
            self.session.add(Users(id_tg=id, first_name=first_name, username=last_name))
            self.session.commit()
        self.session.close()


    def add_language(self, id_user, language):
        """Функция для добавления или обновления языка перевода пользователя"""
        check_lang = FuncBD().info_user_language(id_user)
        if not check_lang:
            self.session.add(TranslatorWord(id_user=id_user, language=language))
        else:
            self.session.query(TranslatorWord).filter(TranslatorWord.id_user == id_user).update({'language': language})
        self.session.commit()
        self.session.close()


    def add_token(self, id_user, token):
        '''Добавление токена пользователю в БД'''
        users = self.session.query(Users).filter(Users.id_tg == id_user).update({'yandex_token': token})
        self.session.commit()
        self.session.close()


    def random_words(self, count):
        '''Изъятие случайных слов из БД
        Функция вернет список случайных слов из БД'''
        rand = self.session.query(AllWords)
        self.session.close()
        return random.sample([(el.eng_word, ',  '.join(el.ru_word.split(', ')[:2]), el.id) for el in rand], k=count)


    def user_words(self, id_user, tab, count=100*100):
        '''Изъятие пользовательских слов из БД
        Функция вернет список пользовательских слов из БД'''
        # --- Выбираем таблицу ---
        table = {'_' not in tab: UserWord, '_' in tab: FavoriteWordUser}[1]
        # -- Проверка количества слов в пользовательском словаре / списке избранного
        usersw = self.session.query(table).filter(table.id_user == id_user).order_by(sq.desc(table.id)).limit(count)
        self.session.close()
        return [(el.eng_word, ',  '.join(el.ru_word.split(', ')[:2]), el.id) for el in usersw]


    def user_count_words(self, id_user, tab):
        """Получение информации о количестве слов"""
        table = {'dict': UserWord, 'favorite': FavoriteWordUser}[tab]
        count = self.session.query(sq.func.count(table.id_user)).filter(table.id_user==id_user)
        return count.scalar()


    def add_result_selection(self, id_user, result):
        """Функция сохраняет результат выбора ответа пользователя при переводе слов: верно - неверно"""

        self.session.add(WinRateWord(id_user=id_user, answer=result))
        self.session.commit(), self.session.close()


    def show_result_user(self, id_user):
        """Функция выводит правильные и неправильные ответы пользователя"""
        # Количество правильных слов
        tr = (self.session.query(sq.func.count(WinRateWord.id_user)).
              filter(WinRateWord.id_user == id_user, WinRateWord.answer == 'true'))
        # Количество неправильных слов
        fl = (self.session.query(sq.func.count(WinRateWord.id_user)).
              filter(WinRateWord.id_user == id_user, WinRateWord.answer == 'false'))
        if tr.scalar() == fl.scalar() == 0: return None
        try: return round(tr.scalar() / (fl.scalar() + tr.scalar()), 2)
        except ZeroDivisionError: return 0


    def add_word_user(self, id_word, id_user, ru_word, eng_word, tab):
        '''Добавление слов пользователю в словарь или в избранное
        Функция вернёт True, если слово добавится, False - если слово уже добавлено'''
        table = {'add dict': UserWord, 'add favorite': FavoriteWordUser}[tab]
        usersw = self.session.query(table).filter(table.id_word==id_word, table.id_user==id_user)
        if not [(el.id_word, el.id_user) for el in usersw]:
            users = self. session.add(table(id_word=id_word,
                                            id_user=id_user,
                                            eng_word=eng_word,
                                            ru_word=ru_word))
            self.session.commit(), self.session.close()
            return True
        self.session.close()
        return False


    def delete_word(self, id_user, tab, count, eng_word=None):
        '''Функция для удаления слов из словаря или избранного'''
        table = {'dict': UserWord, 'favorite': FavoriteWordUser}[tab]
        if count == 'all':
            self.session.query(table).filter(table.id_user == id_user).delete()
        elif count == 'one':
            self.session.query(table).filter(table.id_user == id_user, table.eng_word == eng_word).delete()
        self.session.commit(), self.session.close()


    def notif_users(self, id_user=None, all_users=True):
        '''Функция для получения информации об уведомлениях пользователей'''
        # Если all = True, значит информация по уведомлениям берётся о всех пользователях
        if all_users:
            respons = self.session.query(Notifications)
        # Информация о конкретном пользователе
        else:
            respons = self.session.query(Notifications).filter(Notifications.id_user == id_user)
        return [(i.id_user, i.notifications) for i in respons]


    def update_notif(self, id_user, notif):
        '''Функция для установки и отключения уведомлений'''
        # --- Если пользователя ещё нет в таблице, то он добавляется ---
        check_user = FuncBD().notif_users(id_user, all_users=False)
        if not check_user:
            self.session.add(Notifications(id_user=id_user, notifications=notif))
        self.session.query(Notifications).filter(Notifications.id_user == id_user).update({'notifications': notif})
        self.session.commit(), self.session.close()
