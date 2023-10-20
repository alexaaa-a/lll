import telebot
from telebot import custom_filters
from telebot import StateMemoryStorage
from telebot.handler_backends import StatesGroup, State
import datetime
import random


state_storage = StateMemoryStorage()
# Вставить свой токет или оставить как есть, тогда мы создадим его сами
bot = telebot.TeleBot("6313327483:AAEAp2mZfmUxE1mr5snuKQqVtjqdeUjaBlY", state_storage=state_storage, parse_mode='Markdown')

baza_id = {}
kategory = {"Домашние дела": ["помыть посуду", "приготовить еду"],
            "Школьные дела": ["сделать уроки", "приготовить рюкзак"]}
RANDOM_TASKS = ["помыть посуду", "приготовить еду", "сделать уроки", "приготовить рюкзак"]


def get_kategory(input):
    get_kat = ""
    not_get_kat = " -@данной категории нет"
    for i in kategory:
        if input in kategory[i]:
            get_kat = f' -@{i}'
            break
    if get_kat:
        return get_kat
    else:
        return not_get_kat


def is_valid_date(date_string):
    if date_string in ["сегодня", "завтра"]:
        if date_string == "сегодня":
            date_string = datetime.date.today().strftime('%d.%m.%Y')
        else:
            date_string = str((datetime.date.today() + datetime.timedelta(days=1)).strftime('%d.%m.%Y'))
    try:
        datetime.datetime.strptime(date_string, '%d.%m.%Y')
        return True
    except ValueError:
        return False


def get_date_slova(date):
    if date == datetime.date.today().strftime('%d.%m.%Y'):
        return "сегодня"
    if date == str((datetime.date.today() + datetime.timedelta(days=1)).strftime('%d.%m.%Y')):
        return "завтра"
    else:
        return date


def get_date_ddmmyyyy(date):
    if date == "сегодня":
        return datetime.date.today().strftime('%d.%m.%Y')
    if date == "завтра":
        return str((datetime.date.today() + datetime.timedelta(days=1)).strftime('%d.%m.%Y'))
    else:
        return date


class PollState(StatesGroup):
    name = State()
    age = State()


class HelpState(StatesGroup):
    wait_text = State()


text_poll = "Что ты умеешь делать?"
text_button_1 = "Добавить задачу"  # Можно менять текст
text_button_2 = "Посмотреть задачу"  # Можно менять текст
text_button_3 = "Random"  # Можно менять текст


menu_keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)

menu_keyboard.add(
    telebot.types.KeyboardButton(
        text_poll,
    )
)

menu_keyboard.add(
    telebot.types.KeyboardButton(
        text_button_1,
    )
)

menu_keyboard.add(
    telebot.types.KeyboardButton(
        text_button_2,
    ),
    telebot.types.KeyboardButton(
        text_button_3,
    )
)


@bot.message_handler(state="*", commands=['start'])
def start_ex(message):
    bot.send_message(
        message.chat.id,
        f'Привет, *{message.chat.first_name}*! Что будем делать?',  # Можно менять текст
        reply_markup=menu_keyboard)


@bot.message_handler(func=lambda message: text_poll == message.text)
def first(message):
    bot.send_message(message.chat.id, 'Супер! Я _бот_, который добавляет твои задачи на день какой ты хочешь. Как тебя зовут?')  # Можно менять текст
    bot.set_state(message.from_user.id, PollState.name, message.chat.id)


@bot.message_handler(state=PollState.name)
def name(message):
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['name'] = message.text
    bot.send_message(message.chat.id, 'Супер! [Нажми](https://github.com/Ivan-Sch)- тут мои рабочие коды. Как тебе?')  # Можно менять текст
    bot.set_state(message.from_user.id, PollState.age, message.chat.id)


@bot.message_handler(state=PollState.age)
def age(message):
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['age'] = message.text
    bot.send_message(message.chat.id, 'Спасибо за использование меня!', reply_markup=menu_keyboard)  # Можно менять текст
    bot.delete_state(message.from_user.id, message.chat.id)


@bot.message_handler(func=lambda message: text_button_1 == message.text)
def help_command(message):
    bot.send_message(message.chat.id, 'Укажите дату:')
    bot.register_next_step_handler(message, get_date)


# Обработчик следующего шага - получение даты
def get_date(message):
    date = message.text.lower()
    if not is_valid_date(date):
        text = "Ошибка команды."
        bot.send_message(message.chat.id, text)
    else:
        date = get_date_ddmmyyyy(date)
        bot.send_message(message.chat.id, f'Укажите, какую задачу вы хотите добавить на дату *"{date}"*:')
        bot.register_next_step_handler(message, add_todo, date, message.chat.id)


def add_todo(message, date, id):
    if type(message) is telebot.types.Message:
        task = message.text
    else:
        task = message

    if id not in baza_id:
        baza_id[id] = {}
    if date in baza_id[id]:
        baza_id[id][date].append(task)
    else:
        baza_id[id][date] = []
        baza_id[id][date].append(task)
    bot.send_message(id, f'Задача *"{task}"* добавлена на _"{date}"_.')


@bot.message_handler(func=lambda message: text_button_2 == message.text)
def help_command(message):
    bot.send_message(message.chat.id, 'Укажите дату:')
    bot.register_next_step_handler(message, get_date_show)


# Обработчик следующего шага - получение даты
def get_date_show(message):
    date = message.text.lower()
    if not is_valid_date(date):
        text = "Ошибка команды."
    else:
        date = get_date_ddmmyyyy(date)
        text = ""
        if message.chat.id not in baza_id:
            baza_id[message.chat.id] = {}
        if date in baza_id[message.chat.id]:
            text = get_date_slova(date).upper() + "\n"
            for task in baza_id[message.chat.id][date]:
                text = f'*{text}* > {task} _{get_kategory(task)}_ \n'
        else:
            text = "Задач на эту дату нет."
    bot.send_message(message.chat.id, text)


@bot.message_handler(func=lambda message: text_button_3 == message.text)
def help_command(message):
    date = "сегодня"
    task = random.choice(RANDOM_TASKS)
    add_todo(task, get_date_ddmmyyyy(date), message.chat.id)  # Можно менять текст


@bot.message_handler(commands=["rez"])
def rez(message):
    bot.send_message(message.chat.id, str(baza_id))


bot.add_custom_filter(custom_filters.StateFilter(bot))
bot.add_custom_filter(custom_filters.TextMatchFilter())

bot.infinity_polling()



