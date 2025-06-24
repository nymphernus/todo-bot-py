import random
import telebot
import sqlite3
import os
from datetime import datetime
from dotenv import load_dotenv
from database import *

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

load_dotenv()

bot = telebot.TeleBot(os.getenv("TOKEN"))

connection = sqlite3.connect('list.db', check_same_thread=False)
cursor = connection.cursor()

def db_create():
    create_user_table(cursor)
    create_buylist_table(cursor)
    create_buy_table(cursor)

current_lists = {}

# Начало
@bot.message_handler(commands=['start'])
def send_welcome(message):
    msg = bot.send_message(message.chat.id, "Привет")

# Регистрация
@bot.message_handler(commands=['reg'])
def user_registration(message):
    try:
        res = cursor.execute(check_user_link, (message.from_user.id,)).fetchone()
        if res is not None:
            msg = bot.send_message(message.chat.id, f"Привет, {res[0]}")
        else:
            msg = bot.send_message(message.chat.id, "Как тебя зовут?")
            bot.register_next_step_handler(msg, process_reg)
    except Exception as e:
        handle_error(message, e)

def process_reg(message):
    try:
        usr_value = (message.text, message.from_user.id)
        cursor.execute(add_usr_link, usr_value)
        connection.commit()
        bot.send_message(message.chat.id, 'Успешно')
    except Exception as e:
        handle_error(message, e)




# Добавить продукты
@bot.message_handler(commands=['newlist'])
def create_list(message):
    try:
        list_seed = ''.join(random.choice(str(message.chat.id) + "0123456789" + str(datetime.now().microsecond)) for _ in range(5))

        cursor.execute(add_buylist_link, (f"Список {list_seed}",))
        current_lists[message.chat.id] =  cursor.lastrowid
        connection.commit()

        msg = bot.send_message(message.chat.id, "Введите продукты по одному (Название Кол-во):")
        bot.register_next_step_handler(msg, add_product)
    except Exception as e:
        handle_error(message, e)

def add_product(message):
    try:
        if message.text.lower() == "/done":
            close_list(message)
            return
        
        last_index = message.text.strip().rfind(' ')
        if last_index== -1:
            bot.send_message(message.chat.id, "Неверный формат")
            bot.register_next_step_handler(message, add_product)
            return
        
        product_name = message.text[:last_index].strip()
        quantity = int(message.text[last_index+1:].strip())
        list_id = current_lists[message.chat.id]

        cursor.execute(add_buy_link, (product_name, quantity, list_id))
        connection.commit()

        bot.register_next_step_handler(message, add_product)

    except Exception as e:
        handle_error(message, e)

def close_list(message):
    try:
        res = cursor.execute(check_buylist_link, (current_lists[message.chat.id],)).fetchone()
        if res is None:
            cursor.execute(del_buylist_link, (current_lists[message.chat.id],))
            connection.commit()
            bot.send_message(message.chat.id, "Список пуст. Удаление.")
        else:
            bot.send_message(message.chat.id, "Список создан. Заполнен.")
        del current_lists[message.chat.id]
        
    except Exception as e:
        handle_error(message, e)




#Посмотреть списки
@bot.message_handler(commands=['viewlist'])
def view_list(message):
    try:
        rows = cursor.execute(view_buylist_link).fetchall()
        if len(rows) == 0:
            bot.send_message(message.chat.id, "Списки отсутствуют.")
        else:
            markup = InlineKeyboardMarkup()
            for row in rows:
                btn = InlineKeyboardButton(f"{row[1]}", callback_data = f"view_{row[0]}")
                markup.add(btn)
                
            bot.send_message(message.chat.id, "Доступные списки 🛒", reply_markup=markup)
    except Exception as e:
        handle_error(message, e)

@bot.callback_query_handler(func=lambda call: call.data.startswith('view_'))
def show_list_content(call):
    try:
        list_id = call.data.split("_")[1]
        items = cursor.execute(view_buy_link, (list_id,)).fetchall()
        
        if len(items) == 0:
            bot.answer_callback_query(call.id, "Список пуст.")
        else:
            response = f"Содержимое списка 🍖\n\n"
            for item in items:
                response += f"✨ {item[0]} - {item[1]} шт\n"
            del_markup = InlineKeyboardMarkup()
            del_btn = InlineKeyboardButton("Удалить список", callback_data = f"delete_{list_id}")
            del_markup.add(del_btn)
            
            bot.edit_message_text(response, call.message.chat.id, call.message.message_id, reply_markup=del_markup)
    except Exception as e:
        handle_error(call.message, e)


@bot.callback_query_handler(func=lambda call: call.data.startswith('delete_'))
def delete_list(call):
    try:
        list_id = call.data.split("_")[1]
        
        cursor.execute(del_buylist_link, (list_id,))
        connection.commit()
        
        bot.answer_callback_query(call.id, "Список удалён") #
        bot.delete_message(call.message.chat.id, call.message.message_id) #
    except Exception as e:
        handle_error(call.message, e)











def handle_error(message, err):
    bot.send_message(message.chat.id, "Ошибка")
    print(f"Ошибка: {err}")

if __name__ == "__main__":
    db_create()
    bot.polling(non_stop=True)