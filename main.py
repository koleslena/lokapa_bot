import telebot
from telebot.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove, KeyboardButton
import datetime
import os
import logging
from challenge_data import Challenge, SIVA_NAME, QUESTION, QUESTION_ANSWERS, read_challenge, save_challenge
from sivaname import check_siva_name

logger = telebot.logger

formatter = '[%(asctime)s] %(levelname)8s --- %(message)s (%(filename)s:%(lineno)s)'
logging.basicConfig(
    filename=f'lokapa_bot-from-{datetime.datetime.now().date()}.log',
    filemode='w',
    format=formatter,
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.WARNING
)

TOKEN = os.environ.get("lokapa_bot_token")
ADMIN_PASS = os.environ.get("lokapa_bot_secret")

bot = telebot.TeleBot(TOKEN, parse_mode='HTML')

GET_URL = "Получить ссылку"


ch_dict = {}
passwords = {}

def clean_text(text):
    return text.lstrip().rstrip().replace('\n', '') if text else ""

def check_answer(ans, ch):
    if ch.question_type == SIVA_NAME:
        return check_siva_name(ans, ch.sivaname)
    else:
        return ans == ch.right_answer

def check_password(chat_id):
    password = passwords[chat_id]
    return password == ADMIN_PASS

# Handle '/admin'
@bot.message_handler(commands=['admin'])
def handle_admin(message):
    admin_hello(message)

def admin_hello(message):
    passwords[message.chat.id] = ''
    markup = InlineKeyboardMarkup()
    markup.row_width = 3
    markup.add(
        InlineKeyboardButton("1", callback_data='1'), InlineKeyboardButton("2", callback_data='2'),
        InlineKeyboardButton("3", callback_data='3'), InlineKeyboardButton("4", callback_data='4'),
        InlineKeyboardButton("5", callback_data='5'), InlineKeyboardButton("6", callback_data='6'),
        InlineKeyboardButton("7", callback_data='7'), InlineKeyboardButton("8", callback_data='8'),
        InlineKeyboardButton("9", callback_data='9'), InlineKeyboardButton("0", callback_data='0'))
    msg = bot.reply_to(message, f"Введите код", reply_markup=markup)

def process_password_step(message):
    chat_id = message.chat.id
    if check_password(chat_id):
        passwords[chat_id] = ''
        msg = bot.reply_to(message, f"""\
        Введите новую ссылку \
        """)
        bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=message.id, reply_markup=InlineKeyboardMarkup())
        bot.register_next_step_handler(msg, process_url)
    else:
        msg = bot.reply_to(message, f"""\
        Введен неверный код. Попробуйте еще раз \
        """)
        bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=message.id, reply_markup=InlineKeyboardMarkup())
        admin_hello(message)

def process_url(message):
    if len(message.text) > 0:
        chat_id = message.chat.id
        ch = Challenge(clean_text(message.text))
        ch_dict[chat_id] = ch
        markup = InlineKeyboardMarkup()
        markup.row_width = 1
        markup.add(
            InlineKeyboardButton("Имя Шивы", callback_data=SIVA_NAME),
            InlineKeyboardButton("Вопрос с ответами", callback_data=QUESTION_ANSWERS),
            InlineKeyboardButton("Общий вопрос", callback_data=QUESTION))
        msg = bot.reply_to(message, f"Выберите тип вопроса", reply_markup=markup)
    else:
        msg = bot.reply_to(message, f"""\
        Введен пустой url. Попробуйте еще раз \
        """)
        bot.register_next_step_handler(msg, process_url)

def process_question_text(message):
    if len(message.text) > 0:
        chat_id = message.chat.id
        ch_dict[chat_id].question = clean_text(message.text)

        if ch_dict[chat_id].question_type == QUESTION:
            msg = bot.reply_to(message, f"""\
            Введите верный ответ \
            """)
            bot.register_next_step_handler(msg, process_right_answer)
        else:
            msg = bot.reply_to(message, f"""\
            Введите ответы, разделяя их знаком ; \
            """)
            bot.register_next_step_handler(msg, process_answers)
    else:
        msg = bot.reply_to(message, f"""\
        Введен пустой вопрос. Попробуйте еще раз \
        """)
        bot.register_next_step_handler(msg, process_question_text)

def process_answers(message):
    if len(message.text) > 0:
        chat_id = message.chat.id
        ch_dict[chat_id].answers = [clean_text(x) for x in message.text.split(';')]
        msg = bot.reply_to(message, f"""\
            Введите верный ответ \
            """)
        bot.register_next_step_handler(msg, process_right_answer)
    else:
        msg = bot.reply_to(message, f"""\
        Введен пустой список ответов. Попробуйте еще раз \
        """)
        bot.register_next_step_handler(msg, process_answers)

def process_right_answer(message):
    if len(message.text) > 0:
        chat_id = message.chat.id
        ch_dict[chat_id].right_answer = clean_text(message.text)
        process_save(message)
    else:
        msg = bot.reply_to(message, f"""\
        Введен пустой ответ. Попробуйте еще раз \
        """)
        bot.register_next_step_handler(msg, process_right_answer)

def process_siva_name(message):
    if len(message.text) > 0 and message.text.isdigit() and int(message.text) >= 1 and int(message.text) <= 108:
        chat_id = message.chat.id
        ch_dict[chat_id].sivaname = int(clean_text(message.text))
        ch_dict[chat_id].question_type = SIVA_NAME
        process_save(message)
    else:
        msg = bot.reply_to(message, f"""\
        Введено неверное число. Попробуйте еще раз \
        """)
        bot.register_next_step_handler(msg, process_siva_name)

def process_save(message):
    chat_id = message.chat.id
    ch = ch_dict[chat_id]
    save_challenge(ch)
    bot.send_message(message.from_user.id, f"""\
        Новые данные сохранены. \
        \n\n{ch.url} \
        \n\n{ch.question if ch.question else ch.sivaname} \
        \n\n{'; '.join(ch.answers) if ch.answers else ''}
        \n\n{ch.right_answer if ch.right_answer else ''}
        """)
    
def gen_main_menu():
    markup = ReplyKeyboardMarkup(True, False)
    markup.add(KeyboardButton(GET_URL))
    return markup

# Handle '/cancel'
@bot.message_handler(commands=['cancel'])
def send_cancel(message):
    markup = ReplyKeyboardRemove()
    msg = bot.send_message(message.from_user.id, f"""\
        Отмена \
        """, reply_markup=markup)

# Handle '/start'
@bot.message_handler(commands=['start'])
def send_welcome(message):
    msg = bot.send_message(message.from_user.id, f"""\
        Привет, <i>{message.from_user.first_name}</i>. Я LokaPaBot. \
        \n\nЗдесь вы можете получить ссылку на занятие. \
        \n\nЧтобы получить ссылку жмите на кнопку {GET_URL}. \
        \n\nПомощь /help. \
        """, reply_markup=gen_main_menu())

@bot.message_handler(func=lambda message: message.text == GET_URL)
def process_ask_question(message):
    ch = read_challenge()
    question = ch.question
    answers = ch.answers
    markup = InlineKeyboardMarkup()
    if ch.question_type == QUESTION_ANSWERS:
        markup = InlineKeyboardMarkup()
        markup.row_width = 1
        for ans in answers:
            markup.add(InlineKeyboardButton(ans, callback_data=ans))
    elif ch.question_type == SIVA_NAME:
        question = f'Напишите {ch.sivaname}е имя Шивы на деванагари, iast или hk'
        
    msg = bot.send_message(message.from_user.id, f"""\
        \n\nЧтобы получить ссылку ответьте на вопрос. \
        \n\n{question} \
        """, reply_markup=markup)

# Handle '/help'
@bot.message_handler(commands=['help'])
def send_help(message):
    msg = bot.send_message(message.from_user.id, f"""\
        Привет, <i>{message.from_user.first_name}</i>. Я LokaPaBot. \
        \n\nЯ выдаю ссылки на занятия. \
        \n\nЗдесь вы можете получить ссылку на занятие. \
        \n\nЖмите на кнопку {GET_URL}. \
        """, reply_markup=gen_main_menu())


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    try:
        if len(call.data) > 0 and call.data.isdigit() and int(call.data) in range(10):
            passwords[call.message.chat.id] += call.data
            password = passwords[call.message.chat.id]
            if len(password) == 4:
                process_password_step(call.message)

        elif call.data == SIVA_NAME:
            msg = bot.reply_to(call.message, f"Введите номер имени Шивы")
            bot.register_next_step_handler(msg, process_siva_name)

        elif call.data == QUESTION or call.data == QUESTION_ANSWERS:
            chat_id = call.message.chat.id
            ch_dict[chat_id].question_type = call.data
            msg = bot.reply_to(call.message, f"Введите новый вопрос")
            bot.register_next_step_handler(msg, process_question_text)

        else:
            answer(call.data, call.message)
    except:
        msg = bot.send_message(call.from_user.id, 'Что-то пошло не так. Попробуйте еще раз.')
    
def answer(ans, message):
    ch = read_challenge()
    if check_answer(ans, ch):
        msg = bot.reply_to(message, f"Ссылка {ch.url}")
    else:
        msg = bot.reply_to(message, "Ответ неправильный, увы. Попробуете еще раз?")
        bot.register_next_step_handler(msg, process_ask_question)
    if ch.question_type == QUESTION_ANSWERS:
        bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=message.id, reply_markup=InlineKeyboardMarkup())

@bot.edited_message_handler(func=lambda message: True)
def handle_edited_message(message):
    answer(message.text, message)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    answer(message.text, message)


bot.polling(none_stop=True, interval=0)
