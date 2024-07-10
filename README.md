# Программа для создания телеграм бота по изучению английских слов

### _Техническая документация находится в файле 'Code Documentation.md'._

## Настройка по установке:
- на компьютере должен быть установлен Python последней версии и База данных PostgreSQL
- установить актуальные версии библиотек (находятся в файле requirements.txt, сделать можно через консоль за счет команды  pip install -r requirements.txt)
- заполнить необходимую информацию в файле info.json:
  
  1) login, password, name_bd - логин, пароль и имя от баззы данных в postgreSQL;
  2) token_bot - токен бота, который можно получить в тг у бота https://t.me/BotFather.

- после вставки данных о БД необходимо один раз запустить скрипт "scriptDB.py' для установки базы данных. Повторный запуск в будущем приведёт к перезаписи БД !!
- для включения бота должны быть запущены два скрипта - main.py и notifications.py
- список слов будут загружены с файла words.txt в папке BaseData, в файле находится 2000 популярных слов в английском языке. При необходимости можно вставить свой список слов. Вставка происходит в файле по пути BaseData/createBD, функция loads_words (строка 46-60)

## Возможности бота:
Для начала работы с ботом необходимо прописать команду /start, после чего будет открыто главное меню. Основное взаимодействие с ботом происходит через данное меню.

### _Изучение слов:_
- бот в сообщении выводит слово на английском и даёт 4 слова на выбор, 1 из них правильно. При нажатии на слово, бот уведомит, правильно ли был выбран перевод.
- клавиша "добавить в словарь": слово добавляется к пользователю в словарь
- клавиша "добавить в избранное": слово добавляется к пользователю в список избранного

### _Добавленные слова:_
- клавиша "словарь" или "избранное" - открывается меню с выбором действий: можно повторять добавленные слова или вывести их спосок по алфавиту / по последним добавленным. Клавиша "Удалить слова" полностью удалит слова из пользовательского словаря / списка избранного
- клавиша "сохранить на яндекс диск" - перед загрузкой на яндекс диск бот уведомит о том, что отсутствует token от яндекс диска. При его получении, токен можно загрузить к боту и он сможет отправлять список добавленных слов на Яндекс Диск пользователю

### _Переводчик:_
Бот предложит выбрать тип первода слов: с русского на английский и наоборот. После чего боту можно отправлять слова и он будет их переводить.

**Важно**: _данная функция подразумевает в себе "словарь", поэтому бот умеет переводить только отдельные слова, а не предложения_

### _Информация:_
В данном разделе бот отправит информацию о пользователе имя, id, никнем. Так же покажет количество слов, которые пользователь добавил к себе в словарь или избранное, язык перевода (в чате), процент правильно выбранных слов и время уведомлений

### _Уведомления:_
В данном разделе можно включить или выключить уведомления (время указано по МСК). В выбранное время бот будет отправлять напоминаку о том, что пришло время повторить слова.

------
