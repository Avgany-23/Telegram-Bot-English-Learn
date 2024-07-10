import re
import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship


basic = declarative_base()


class Users(basic):
    '''Таблица пользователей'''
    __tablename__ = 'users'

    id = sq.Column(sq.Integer, sq.Sequence('user_id_seq'), autoincrement="auto")
    id_tg = sq.Column(sq.BigInteger, primary_key=True)
    first_name = sq.Column(sq.Text)
    username = sq.Column(sq.Text)
    yandex_token = sq.Column(sq.Text)


class AllWords(basic):
    ''''Таблица всех слов'''
    __tablename__ = 'allwords'

    id = sq.Column(sq.Integer, primary_key=True)
    eng_word = sq.Column(sq.Text)
    ru_word = sq.Column(sq.Text)
    tr = sq.Column(sq.Text)


class UserWord(basic):
    '''Таблица словарных слов пользователей'''
    __tablename__ = 'userword'

    id = sq.Column(sq.Integer, primary_key=True)
    id_word = sq.Column(sq.BigInteger, sq.ForeignKey('allwords.id'))
    id_user = sq.Column(sq.BigInteger, sq.ForeignKey('users.id_tg'))
    eng_word = sq.Column(sq.Text)
    ru_word = sq.Column(sq.Text)

    allw = relationship(AllWords, backref='aw')
    use = relationship(Users, backref='us')

class FavoriteWordUser(basic):
    '''Таблица изранных слов пользователей'''
    __tablename__  = 'favoriteworduser'

    id = sq.Column(sq.Integer, primary_key=True)
    id_word = sq.Column(sq.BigInteger, sq.ForeignKey('allwords.id'))
    id_user = sq.Column(sq.BigInteger, sq.ForeignKey('users.id_tg'))
    eng_word = sq.Column(sq.Text)
    ru_word = sq.Column(sq.Text)

    allw1 = relationship(AllWords, backref='aw1')
    use1 = relationship(Users, backref='us1')

class TranslatorWord(basic):
    '''Установка языка переводчика пользователей'''
    __tablename__  = 'translatorword'

    id = sq.Column(sq.Integer, primary_key=True)
    id_user = sq.Column(sq.BigInteger, sq.ForeignKey('users.id_tg'))
    language = sq.Column(sq.Text)

    use11 = relationship(Users, backref='us11')

class WinRateWord(basic):
    '''Таблица с процентами правильно отвеченных слов пользователями'''
    __tablename__ = 'winrateword'

    id = sq.Column(sq.Integer, primary_key=True)
    id_user = sq.Column(sq.BigInteger, sq.ForeignKey('users.id_tg'))
    answer = sq.Column(sq.Text)

    wr = relationship(Users, backref='wr')


class Notifications(basic):
    '''Таблица уведомлений'''
    __tablename__ = 'notifications'

    id = sq.Column(sq.Integer, primary_key=True)
    id_user = sq.Column(sq.BigInteger, sq.ForeignKey('users.id_tg'))
    notifications = sq.Column(sq.Text, default='no')

    notf = relationship(Users, backref='notf')

