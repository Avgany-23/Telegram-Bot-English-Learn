from telebot import types
from BaseData.createBD import create_bd, loads_words
from Scripts.func_sc import *
from Scripts.bd_func import *
import telebot
import json
import os
import re


# --- Создание Базы Данных и загрузка слов ---
with open('info.json', encoding='utf') as f:
    info_js = json.load(f)
    if not info_js['postgreSQL']['create']:             # Если База Данных не создана, то создаем и загружаем слова
        puth = os.path.join(os.getcwd(), 'info.json')   # Получение пути к файлу с информацией о БД
        create_bd(puth)                                 # Создание БД
        loads_words(puth)                               # Загрузка слов в БД

bot = telebot.TeleBot(info_js['token_bot'])             # Подключение к Боту


# --- Обработка команды /start ---
@bot.message_handler(commands=['start'])
def start_bot(message):
    """Главное меню бота"""
    # --- Сохранение пользователя в Базу Данных ---
    FuncBD().add_user(message.chat.id, message.from_user.first_name, message.from_user.username)
    FuncBD().update_notif(message.chat.id, 'no')
    # --- Вывод главного меню бота ---
    Inline_Main_Menu(message.chat.id, bot)


# ------- Ответы с Inline клавиатуры -------
@bot.callback_query_handler(func=lambda cb: True)
def callback_inline_start(callback):
    id_user = callback.message.chat.id
    id_mess = callback.message.message_id
    cb_dat = callback.data
    # ----------- Действия -----------
    if cb_dat == 'main menu':                                   # Вызов главного меню
        Inline_Main_Menu(id_user, bot, show='replace', id_mess=id_mess)
    if cb_dat == 'none':                                        # Для пустых Inline клавиш
        empty_response(bot, callback.id)
    if cb_dat in ('learn', 'next word'):                        # Вызов меню с изучением слов
        Inline_Learn_All_Words(id_user, bot, 4, id_mess)
    if cb_dat in ('add dict', 'add favorite'):                  # Добавляет слова в словарь или избранное
        add_word_to_user(id_user, cb_dat, callback.id, bot)
    if re.findall(r'word\d{1,2}', cb_dat):                      # Для определения правильности ответа на перевод слова
        check_word_learn(id_user, bot, cb_dat, callback.id)
    if cb_dat in ('user_dict'):                                 # Вызов меню добавленных пользователем слов
        Inline_Add_Words(id_user, bot, id_mess)
    if cb_dat in ('words_dict', 'words_favorite'):              # Вызов меню словаря / списка избранного
        Inline_Learn_User_Words(id_user, id_mess, bot, cb_dat)
    if re.findall(r'action[123_]{1,2}', cb_dat):                # Вызов меню выбора количества слова
        user_dict_count(id_user, id_mess, bot, cb_dat)
    if re.findall(r'repeat\d{2}|all', cb_dat):                  # Повторение или просмотра пользовательских слов
        user_words_repeat_or_print(id_user, id_mess, bot, cb_dat, callback.id, count=4)
    if cb_dat == 'next word repeat':                            # Для вывода следующего слова пользователя при повторе
        user_words_repeat_or_print_NEXT(id_user, bot, id_mess, count=4)
    if re.findall(r'del_.+', cb_dat):                           # Для удаления слов
        delete_user_word(id_user, bot, id_mess, cb_dat, callback.id)
    if cb_dat == 'save_yandex':                                 # Для отправки слов на Яндекс диск
        Inline_Save(bot, id_user, id_mess)
    if cb_dat in ('save_yandex dict', 'save_yandex favotire'):  # Меню для выбора отправляемых слов
        send_yand_disk(id_user, bot, id_mess, cb_dat, callback.id)
    if cb_dat == 'translate':                                   # Меню для выбора перевода слов в чате
        Inline_Translator_menu(bot, id_user, id_mess)
    if cb_dat in ('ru-en', 'en-ru'):                            # Установка языка перевода. Оповещение бота об этом
        translate_installation(bot, id_user, cb_dat)
    if cb_dat == 'info':                                        # Вывод информации пользователя
        info_user(bot, id_user, id_mess)
    if cb_dat == 'notif':                                       # Меню с установкой уведомлений
        Inline_Notifications(bot, id_user, id_mess)
    if re.findall(r'time\d{2}|off_notif', cb_dat):              # Установка/отключение уведомлений
        notifications(id_user, bot, cb_dat, callback.id)



# ------- Ответы на текстовые сообщения пользователя -------
@bot.message_handler(content_types=['text'])
def another_message(message):
    text = message.text
    id_user = message.chat.id

    # ----------- Действия -----------
    if re.findall(r'token:\s*[\w]{5,}\s*', text):           # Если пользователь пытается добавить токен
        add_yandex_token(bot, text, id_user)
    else:
        translate_chat_word(bot, id_user, text)             # Перевод слов

bot.polling()