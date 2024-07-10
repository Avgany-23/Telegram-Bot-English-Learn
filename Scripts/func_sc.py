import json
import random
import re
from Scripts.add_words_yandex import *
from telebot import types
from Scripts.bd_func import *
from BaseData.models import *
from string import ascii_letters
import os


def Inline_Main_Menu(chat_id, bot, show='send', id_mess=None):
    """Функция для Inline клавиатуры главного меню бота"""
    # --- Создание и настройка Inline клавиатуры ---
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(*[types.InlineKeyboardButton(text='🟣🟣 главное меню 🟣🟣', callback_data='none'),
             types.InlineKeyboardButton(text='Изучение слов 🔀', callback_data='learn'),
             types.InlineKeyboardButton(text='Добавленные слова 📚', callback_data='user_dict'),
             types.InlineKeyboardButton(text='Переводчик 🔎', callback_data='translate'),
             types.InlineKeyboardButton(text='Информация ℹ️', callback_data='info'),
             types.InlineKeyboardButton(text='Уведомления 🚨', callback_data='notif'),
             types.InlineKeyboardButton(text='--- ', callback_data='none')])
    if show == 'send':                                      # Отправляет клавиатуру (новым сообщением)
        bot.send_message(chat_id, 'Выберите действие', reply_markup=markup)
    elif show == 'replace':                                 # Заменяет текущую клавиатуру на клавиатуру главного меню
        bot.edit_message_text(chat_id=chat_id,
                              message_id=id_mess,
                              text='Выберите действие',
                              reply_markup=markup)


def Inline_Learn_All_Words(id_user, bot, count, id_mess, repeat=False):
    """Функция для Inline клавиатуры изучения слов
    repeat = False по умолчанию. Если true, значит слова берутся для повторога из пользовательского списка"""
    # --- Взятие из словаря пользователя четыре случайных слова  ---
    if repeat:
        # Информация для сообщений
        reader = open_file(f"action{id_user}")
        user_action = 'избранного' if '_' in reader['action'] else 'словаря'
        cb_data_delete = 'del_favorit word' if '_' in reader['action'] else 'del_dict word'
        # Считывание слов
        reader = open_file(f"userword{id_user}")
        # Изменение позиции на минус 1
        with open(f'ForProgramm/userword{id_user}.json', 'w', encoding='utf-8') as f:
            json.dump({'words': reader['words'], 'position': reader['position'] - 1}, f, indent=3)

        # --- Если слова закончились, то выход в главное меню ---
        if reader['position'] < 0:
            bot.send_message(id_user, 'Слова для повторения закончились')
            Inline_Main_Menu(id_user, bot, show='replace', id_mess=id_mess)

        cb_data_next = 'next word repeat'           # Для клавиши callback_data, для повторного вызова этих же условий
        text = f"Осталось {choose_plural(reader['position'] + 1, ('слово', 'слова', 'слов'))} 🤩\n" # Дополнительное сообщение
        words = reader['words']                                             # Получение пользовательских слов
        target_word = words[reader['position']][1]                          # Правильное слово перевода на русском
        translate = words[reader['position']][0]                            # Правильное слово перевода на английском
        others = random.sample([i[1] for i in words], k=count - 1) + [words[reader['position']][1]] # слова на английском
        others_ = [f"{i}: {w}" for i, w in enumerate(others, 1)]  # Для вывода слов
        id_word = 0
        kb = [types.InlineKeyboardButton(text=f'--Удалить из {user_action}❌--', callback_data=cb_data_delete)]

    # --- Взятие из общего словаря четыре случайных слова  ---
    else:
        words = FuncBD().random_words(count)    # Получение случайных слов из списка общих слов
        cb_data_next = 'next word'              # Для клавиши callback_data, для повторного вызова этих же условий
        text = ''                               # Дополнительное сообщение
        target_word = words[0][1]               # Правильное слово перевода на русском
        translate = words[0][0]                 # Правильное слово перевода на английском
        others = [i[1] for i in words]          # 4 слова на английском
        random.shuffle(others)                  # Перемешивание слов
        id_word = words[0][2]                   # id слова для добавления в словарь или список избранного
        others_ = [f"{i}: {w}" for i, w in enumerate(others, 1)]    # Для вывода слов
        kb = [types.InlineKeyboardButton(text='в словарь 📒', callback_data='add dict'),
                 types.InlineKeyboardButton(text='в избранное 🧡', callback_data='add favorite')]

    # --- Создание и настройка Inline клавиатуры ---
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(*[types.InlineKeyboardButton(text=word, callback_data=f'word{i}') for i, word in enumerate(others_, 1)])
    markup.row(*kb)
    markup.row(types.InlineKeyboardButton(text='Следующее слово ▶', callback_data=cb_data_next))
    markup.row(types.InlineKeyboardButton(text='➖➖➖Главное меню ➖➖➖', callback_data='main menu'))
    bot.edit_message_text(chat_id=id_user,
                          message_id=id_mess,
                          text=f"{text}Выбери перевод слова:\n🇺🇸 {translate}",
                          reply_markup=markup)

    # --- Сохранение показаных слов для будущего определение того, правильный ли перевод выберет пользователь ---
    with open(f"ForProgramm/word{id_user}.json", 'w', encoding='utf-8') as f:
        dict_word = {'target': {'eng': translate, 'ru': str(target_word), 'id': id_word}, 'all_word': others}
        json.dump(dict_word, f, indent=3)


def Inline_Add_Words(id_user, bot, id_mess):
    "Функция для Inline клавиатуры добавленных слов"
    # --- Создание и настройка Inline клавиатуры ---
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.row(types.InlineKeyboardButton(text='⬇️Меню добавленных слов⬇️', callback_data='none'))
    markup.add(*[types.InlineKeyboardButton(text='Словарь 📖', callback_data='words_dict'),
                 types.InlineKeyboardButton(text='Избранные 🧡', callback_data='words_favorite')])
    markup.row(types.InlineKeyboardButton(text='❇️Сохранить на Яндекс Диск❇️', callback_data='save_yandex'))
    markup.row(types.InlineKeyboardButton(text='🔙 Вернуться назад 🔙', callback_data='main menu'))

    # --- Запуск Inline клавиатуры ---
    bot.edit_message_text(chat_id=id_user,
                          message_id=id_mess,
                          text="Здесь можно просмотреть и начать повторение добавленных вами слов",
                          reply_markup=markup)


def Inline_Learn_User_Words(id_user, id_mess, bot, cb_dat):
    '''Функция для Inline кдавиатуры просмотра меню словаря / избранных слов'''
    # --- Определяется выбранная пользователем клавиша (для правильного callback_data) ---
    table = {'words_dict': 1, 'words_favorite': 0}[cb_dat]

    # --- Определение действия (action1-3 - для словаря, action_1-3 - для списка избранного)
    info_action = [{'action1': 'action1_', 'action2': 'action2_', 'action3': 'action3_'},
                   {'action1': 'action1', 'action2': 'action2', 'action3': 'action3'}][table]

    # --- Создание и настройка Inline клавиатуры ---
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.row(types.InlineKeyboardButton(text=['🧡🧡🧡 Избранное 🧡🧡🧡', '📚📚📚 Словарь 📚📚📚'][table], callback_data='none'))
    markup.row(types.InlineKeyboardButton(text='Начать повторение слов 🔃', callback_data=info_action['action1']))
    markup.row(types.InlineKeyboardButton(text='🔽🔽 Просмотр слов 🔽🔽', callback_data='none'))
    markup.add(*[types.InlineKeyboardButton(text='По алфавиту🔤', callback_data=info_action['action2']),
                 types.InlineKeyboardButton(text='Последние добавленные💠', callback_data=info_action['action3'])])
    markup.row(types.InlineKeyboardButton(text='Удалить слова 🗑🔴', callback_data=['del_f', 'del_du'][table]))
    markup.row(types.InlineKeyboardButton(text='🔙 Вернуться назад 🔙', callback_data='user_dict'))
    markup.row(types.InlineKeyboardButton(text='➖➖➖Главное меню ➖➖➖', callback_data='main menu'))

    # --- Запуск Inline клавиатуры ---
    bot.edit_message_text(chat_id=id_user,
                          message_id=id_mess,
                          text="Выберите действие",
                          reply_markup=markup)


def user_dict_count(id_user, id_mess, bot, cb_dat):
    """Функция Inline клавиатуры выбора количества слов (для повторения или вывода слов из слова / списка избранного"""
    # --- Сохранение предыдущего действия пользователя ---
    with open(f"ForProgramm/action{id_user}.json", 'w', encoding='utf-8') as f:
        json.dump({'action': cb_dat}, f, indent=3)

    # --- Для выбора callback_data кнопки "вернуться назад"
    back_inline = 'words_favorite' if '_' in cb_dat else 'words_dict'

    # --- Создание и настройка Inline клавиатуры ---
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.row(types.InlineKeyboardButton(text='⬇️ Количество слов ⬇️', callback_data='none'))
    markup.add(*[types.InlineKeyboardButton(text='10', callback_data='repeat10'),
                 types.InlineKeyboardButton(text='20', callback_data='repeat20'),
                 types.InlineKeyboardButton(text='30', callback_data='repeat30'),
                 types.InlineKeyboardButton(text='50', callback_data='repeat50')])
    markup.row(types.InlineKeyboardButton(text='все слова', callback_data='all'))
    markup.row(types.InlineKeyboardButton(text='🔙 Вернуться назад 🔙', callback_data=back_inline))
    markup.row(types.InlineKeyboardButton(text='➖➖➖Главное меню ➖➖➖', callback_data='main menu'))

    # --- Запуск Inline клавиатуры ---
    bot.edit_message_text(chat_id=id_user,
                          message_id=id_mess,
                          text="Выберите действие", reply_markup=markup)


def Inline_Save(bot, id_user, id_mess):
    '''Функция для Inline клавиатуры выбора сохранения слов на яндекс диск'''
    # --- Создание и настройка Inline клавиатуры ---
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.row(types.InlineKeyboardButton(text='⬇️ Список слов ⬇️', callback_data='none'))
    markup.add(*[types.InlineKeyboardButton(text='словарь', callback_data='save_yandex dict'),
                 types.InlineKeyboardButton(text='избранное', callback_data='save_yandex favotire')])
    markup.row(types.InlineKeyboardButton(text='🔙 Вернуться назад 🔙', callback_data='user_dict'))
    markup.row(types.InlineKeyboardButton(text='➖➖➖Главное меню ➖➖➖', callback_data='main menu'))

    # --- Запуск Inline клавиатуры ---
    bot.edit_message_text(chat_id=id_user,
                          message_id=id_mess,
                          text="Выберите действие", reply_markup=markup)


def Inline_Translator_menu(bot, id_user, id_mess):
    """Функция для меню выбора перевода слов в чате"""
    # --- Создание и настройка Inline клавиатуры ---
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.row(types.InlineKeyboardButton(text='⬇️ Выберите перевод ⬇️', callback_data='none'))
    markup.add(*[types.InlineKeyboardButton(text='🇷🇺 👉 🇺🇸', callback_data='ru-en'),
                 types.InlineKeyboardButton(text='🇺🇸 👉 🇷🇺', callback_data='en-ru')])
    markup.row(types.InlineKeyboardButton(text='➖➖➖Главное меню ➖➖➖', callback_data='main menu'))

    # --- Запуск Inline клавиатуры ---
    bot.edit_message_text(chat_id=id_user,
                          message_id=id_mess,
                          text="Выберите действие", reply_markup=markup)


def Inline_Notifications(bot, id_user, id_mess):
    """Функция для Inline клавиатуры по установке уведомлений"""
    # --- Создание и настройка Inline клавиатуры ---
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.row(types.InlineKeyboardButton(text='⬇️ Когда отправлять ? ⬇️', callback_data='none'))
    markup.add(*[types.InlineKeyboardButton(text='00:00', callback_data='time00'),
                 types.InlineKeyboardButton(text='12:00', callback_data='time12'),
                 types.InlineKeyboardButton(text='15:00', callback_data='time15'),
                 types.InlineKeyboardButton(text='18:00', callback_data='time18'),
                 types.InlineKeyboardButton(text='20:00', callback_data='time20'),
                 types.InlineKeyboardButton(text='22:00', callback_data='time22')])
    markup.row(types.InlineKeyboardButton(text='❌выключить❌', callback_data='off_notif'))
    markup.row(types.InlineKeyboardButton(text='➖➖➖Главное меню ➖➖➖', callback_data='main menu'))

    # --- Запуск Inline клавиатуры ---
    bot.edit_message_text(chat_id=id_user,
                          message_id=id_mess,
                          text="Выберите действие", reply_markup=markup)


def notifications(id_user, bot, cb_dat, call_id):
    """Функция включает или выключает уведомления"""
    notif = {'time00': '00:00', 'time12': '12:00', 'time15': '15:00',
             'time18': '18:00', 'time20': '20:00', 'time22': '22:00',
             'off_notif': 'no'}[cb_dat]
    # Выбор оповещение об установке / отключения уведомления
    if notif == 'no':
        mes = f"🙅‍♂️Уведомления выключены🙅‍♂️"
    else:
        mes = f"Уведомления включены на {choose_plural(int(notif[-5:-3]), ('час', 'часа', 'часов'), ':00')}"
    FuncBD().update_notif(id_user, notif)       # Обновление статуса уведомлений в БД
    bot.answer_callback_query(call_id, mes)     # Уведомления бота об установке / отключения уведомления


def user_words_repeat_or_print(id_user, id_mess, bot, cb_dat, cb_id, count=4):
    '''Вызов меню повторения или вывод пользовательских слов'''
    # --- Изъятие сохраненного действия ---
    user_action = open_file(f"action{id_user}")['action']
    count_words = {'repeat10': 10, 'repeat20': 20, 'repeat30': 30, 'repeat50': 50, 'all': 5000}[cb_dat]

    # --- Сохранение изъятых из пользовательского списка слов
    words = FuncBD().user_words(id_user, user_action, count_words)
    # Если первое действие, значит повтор пользьзовательских слов
    if '1' in user_action:
        # --- Сохранение изъятых из пользовательского списка слов
        random.shuffle(words)
        # Если слов меньше, чем 4, то повторять слова нельзя
        if len(words) < 4:
            bot.answer_callback_query(cb_id, f"✖️✖️ Недостаточно слов для повторения ✖️✖️\n"
                                             f"{'-' * 14}Добавьте ещё слов в список{'-' * 14}")
            return False
        with open(f'ForProgramm/userword{id_user}.json', 'w', encoding='utf-8') as f:
            json.dump({'words': words, 'position': len(words) - 1}, f, indent=3)
        Inline_Learn_All_Words(id_user, bot, count, id_mess, repeat=True)
    else:
        # Если добавленных слов нет, то уведомить об этом
        if not words:
            bot.answer_callback_query(cb_id, f"✖️ Для начала добавьте слова к себе в список ✖️\n")
        # Если добавленные слова есть, то вывести их
        else:
            if '3' in user_action:
                words = words
                message_ = 'последних добавленных слов '
            else:
                words = list(sorted(words, key=lambda x: x[0]))
                message_ = 'слов по алфавиту '
            message1 = 'из словаря 📓' if '_' not in user_action else 'из избранного 💙'
            message1 = message_ + message1
            message2 = [f"{i})🔸eng: {w[0]}\n{' '*11}ru: {w[1]}" for i, w in enumerate(words, 1)]
            bot.send_message(id_user, f"Ваш список  {message1}\n" + '\n'.join(str(i) for i in message2))
            Inline_Main_Menu(id_user, bot, show='send')
            bot.delete_message(id_user, id_mess)


def user_words_repeat_or_print_NEXT(id_user, bot, id_mess, count=4):
    '''Функция для перехода к следующему слову при повторении пользовательских слов'''
    # Получение информации о оставшемся количестве повтора слов
    reader = open_file(f"userword{id_user}")

    # Если слова закончились, то выход в главное меню
    if reader['position'] < 0:
        bot.send_message(id_user, 'Слова для повторения закончились')
        bot.delete_message(id_user, id_mess)
        Inline_Main_Menu(id_user, bot, show='send', id_mess=id_mess)
    # Если слова остались, то повторять дальше
    else:
        Inline_Learn_All_Words(id_user, bot, count, id_mess, repeat=True)


def delete_user_word(id_user, bot, id_mess, cb_dat, call_id):
    """Функция для удаления слов пользователя"""
    info = {'del_f': ['favorite', 'all', 'Все слова из избранного удалены ☑️', None],
             'del_du': ['dict', 'all', 'Все слова из словаря удалены ☑️', None],
             'del_favorit word': ['favorite', 'one', 'Слово удалено из избранного ☑️', None],
             'del_dict word': ['dict', 'one', 'Слово удалено из словаря ☑️', None]}[cb_dat]

    # Если слово одно, значит узнать информацию об удаляемом слове
    if info[1] == 'one':
        reader = open_file(f'userword{id_user}')
        info[3] = reader['words'][reader['position'] + 1][0]

    # Процесс удаление и оповещение ботом об этом
    FuncBD().delete_word(id_user, info[0], info[1], info[3])
    bot.answer_callback_query(call_id, f'{info[2]}')


def add_yandex_token(bot, text, id_user):
    """Функция для подключения яндекс токена"""
    token = re.findall(r'token:\s*([\w]{5,})\s*', text)[0]
    if check_connect_to_yandex_disk(token) == 200:
        info = FuncBD().info_user(id_user)
        if info[0][3] == token:             # Если такой токен уже есть, то ничего не происходит
            bot.send_message(id_user, 'Данный токен уже добавлен ❗️❗️❗️')
        elif info[0][3] is None:            # Если никакого токена не было, то новый токен добавляется
            bot.send_message(id_user, 'Токен успешно добавлен ✅')
            FuncBD().add_token(id_user, token)
        else:                               # Если токен уже был, то обновляется на новый
            bot.send_message(id_user, 'Токен успешно изменён 🔄')
            FuncBD().add_token(id_user, token)
    else:                                   # Если подключиться к диску не удалось, значит токен неверный
        bot.send_message(id_user, 'Ошибка в подключении. Вероятно, неверный Токен ❌')


def send_yand_disk(id_user, bot, id_mess, cb_dat, cb_id):
    """"Фугкция для сохранения слов на Яндекс диск"""
    def message():
        bot.send_message(id_user, '❗️❗️❗️ У вас не подключен яндекс токен ❗️❗️❗️\n\n'
                                   'Инструкция для его получения:\n'
                                   'https://yandex.ru/dev/disk/rest\n\n'
                                   'Для подключение или изменения OAuth-токен, введите сообщением в формате\n'
                                   'token: <имя токена>')
    info = FuncBD().info_user(id_user)
    # --- Если токен не добавлен, то бот об этом сообщит ---
    if info[0][3] is None:
        message()
        bot.delete_message(id_user, id_mess)
        Inline_Main_Menu(id_user, bot, show='send', id_mess=id_mess)
    # --- Сохранение на яндекс диск и оповещение об этом в чате. Если слов нет, бот об этом сообщит ---
    else:
        table = {'save_yandex dict': 'dict', 'save_yandex favotire': 'favorite'}[cb_dat]
        bot.send_message(id_user, put_yandex_data(info[0][3], id_user, table))


def translate_installation(bot, id_user, cb_dat):
    """Функция для оповещения и установки языка перевода"""
    # --- Выбор оповещения бота ----
    phrase = {'en-ru': 'с английского на русский 🇷🇺 👉 🇺🇸', 'ru-en': 'с русского на английский 🇷🇺 👉 🇺🇸'}[cb_dat]
    # --- Оповещение бота ---
    # Если никакого языка не установлено, то значит он устанавливаеся в первые
    if not FuncBD().info_user_language(id_user):
        bot.send_message(id_user, f'Вы установили перевод {phrase}.\n\n'
                                  f'Теперь бот может переводить отдельные слова ❤️')
    # Если язык уже был выбран, то вывод этого сообщения
    else:
        bot.send_message(id_user, f'Перевод {phrase[:24]} установлен ✅')
    # --- Добавление выбранно языка пользователю в БД
    FuncBD().add_language(id_user, cb_dat)


def translate_chat_word(bot, id_user, text):
    """Функция для перевода слов в чате"""
    # --- Получение информации о установленном языке перевода
    lang = FuncBD().info_user_language(id_user)

    # --- Просто русские буквы :) ---
    ru_letters = 'йцукенгшщзхъфывапролджэячсмитьбюё'
    res_ru_letters = ru_letters + ru_letters.upper()

    # Если язык перевода не установлен, то вывод данного сообщения
    if not lang:
        bot.send_message(id_user, '------------- Пожалуйста, выберите язык перевода -------------\n\n'
                                          '➡️ главное меню ➡️ переводчик ➡️ тип перевода')
    else:
        text = text.encode('utf-8').decode('utf-8')
        if (lang[0] == 'en-ru' and set(text) < set(ascii_letters)) or (lang[0] == 'ru-en' and set(text) < set(res_ru_letters)):
            bot.send_message(id_user, translate_word(text, lang[0]))
        else:
            word = 'английском' if lang[0] == 'en-ru' else 'русском'
            bot.send_message(id_user, f'Пожалуйста, введите слово на {word} и без лишних символов')


def info_user(bot, id_user, id_mess):
    """Функция выводит информацию о пользователе"""
    inf = FuncBD().full_info_user(id_user)
    if inf[5][0][1] == 'no':
        notif_user = 'выключены✖️'
    else:
        notif_user = f"приходят ровно в {choose_plural(int(inf[5][0][1][:2]), ('час', 'часа', 'часов'))} 00 минут по МСК"

    bot.send_message(id_user, f"ℹ️ℹ️ О вас\n"
                              f"--Имя: {inf[0][0][1]}\n"
                              f"--TG имя: {inf[0][0][2]}\n"
                              f"--TG id: {inf[0][0][0]}\n"
                              f"--Количество слов в словаре: {inf[2]}\n"
                              f"--Количество слов в избранном: {inf[3]}\n"
                              f"--Язык перевода слов в чате: {inf[1][0]}\n"
                              f"--Процент правильно выбранных слов: {inf[4]}\n"
                              f"--Уведомления {notif_user}")
    bot.delete_message(id_user, id_mess)
    Inline_Main_Menu(id_user, bot, show='send')


def check_word_learn(id_user, bot, cb_dat, cb_id):
    '''Функция проверяет, правильно ли пользователь перевёл слово'''
    position_word = int(re.findall(r'word(\d{1,2})', cb_dat)[0]) - 1
    reader = open_file(f"word{id_user}")

    # --- Вывод сообщения об правильности выбора слова и сохранение результата для статистики ---
    if reader['target']['ru'] == reader['all_word'][position_word]:
        bot.answer_callback_query(cb_id, '✅✅✅---правильно---✅✅✅')
        FuncBD().add_result_selection(id_user, 'true')
    else:
        bot.answer_callback_query(cb_id, '⛔️⛔️⛔️---неверно---⛔️⛔️⛔️')
        FuncBD().add_result_selection(id_user, 'false')


def empty_response(bot, call_id):
    '''Функция для пустых Inline клавиш'''
    bot.answer_callback_query(call_id, f'👀 Тут ничего нет 👀')


def add_word_to_user(id_user, cb_dat, cb_id, bot):
    """Функция для добавления слов в избранное или словарь"""
    # --- Выбор добавления: в словарь или избранное ---
    info = {'add dict': [UserWord, 'словарь', 'словаре'],
            'add favorite': [FavoriteWordUser, 'избранное', 'избранном']}

    # --- Изъятие сохраненного слова ---
    user_word = open_file(f"word{id_user}")['target']
    # --- Вызов функции для добавления слова ---
    if FuncBD().add_word_user(id_word=user_word['id'],
                           id_user=id_user,
                           ru_word=user_word['ru'],
                           eng_word=user_word['eng'],
                           tab=cb_dat):
        bot.answer_callback_query(cb_id, f"💙 слово добавлено в {info[cb_dat][1]} 💙")           # Ответ бота
    else:
        bot.answer_callback_query(cb_id, f"❌ слово уже есть в {info[cb_dat][2]} ❌")        # Ответ бота


def choose_plural(amount, declensions, dop=''):
    """Функция для склонения слов
    amount - количество, declensions - склонения (кто, кого, сколько)"""
    selector = {
        amount % 10 == 1: 0,
        amount % 10 in [2, 3, 4]: 1,
        amount % 10 in [0, 5, 6, 7, 8, 9]: 2,
        amount % 100 in range(11, 21) : 2
    }
    return f'{amount}{dop} {declensions[selector[True]]}'


def open_file(name, format='.json'):
    '''Функция для открытия файлов'''
    with open(f'ForProgramm/{name}{format}', encoding='utf-8') as f:
        reader = json.load(f)
    return reader


def translate_word(word, language='ru-en'):
    """Функция для перевода слов"""
    url = ('https://dictionary.yandex.net/api/v1/dicservice.json/lookup?key=dict.1.1.'
           '20240514T151055Z.9223e84d46b66584.cb0a6b98a598fa379099758bd12182a5b2ad03a3')
    params = {'lang': language, 'text': word}
    response = requests.get(url, params=params)
    try:
        if language == 'ru-en':
            return f"🇬🇧 en:   {response.json()['def'][0]['tr'][0]['text']}\n🇷🇺 ru:   {word}"
        return f"🇬🇧 en:   {word}\n🇷🇺 ru:   {response.json()['def'][0]['tr'][0]['text']}"
    except:
        return 'Такого слова не нашлось'