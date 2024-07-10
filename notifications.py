from telebot import *
from datetime import datetime
from time import sleep
from Scripts.func_sc import FuncBD
import json


# --- Взятие токена для бота ---
with open('info.json', encoding='utf') as f:
    info_js = json.load(f)

bot = telebot.TeleBot(info_js['token_bot'])             # Подключение к Боту

def time_notif(time, info_time):
    """Функция для отправки уведомлений"""
    info = FuncBD().notif_users(all_users=True)
    for el in info:
        if info_time == el[1]:
            bot.send_message(el[0], '🕘🕘🕘 Время повторять слова 🕘🕘🕘')
    sleep(time * 60 * 60 - 30)

# Отправка уведомлений
while True:
    hour, second = datetime.now().hour, datetime.now().second
    if hour == 0 and second == 0:
        time_notif(12, '00:00')
    if hour == 12 and second == 0:
        time_notif(3, '12:00')
    if hour == 24 and second == 0:
        time_notif(3, '15:00')
    if hour == 18 and second == 0:
        time_notif(2, '18:00')
    if hour == 20 and second == 0:
        time_notif(2, '20:00')
    if hour == 22 and second == 0:
        time_notif(2, '22:00')


bot.polling()