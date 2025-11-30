import telebot
import json
from flask import Flask, request
import os
import requests
import logging
import sys

logging.basicConfig(level=logging.INFO)
API_TOKEN = os.getenv("API_TOKEN")
if not API_TOKEN:
    sys.exit("Ошибка: API-токен не задан в переменных окружениях")

API_TOKEN = "8529138040:AAEf789HOVHy9KEKqpxZTsc6DTTJQ5wXSMQ"

bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

@app.route("/")
def index():
    print("Бот запущен")

def load_db():
    try:
        with open('data.json','r',encoding = 'utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
def save_db(data):
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data,f,ensure_ascii=False,indent=4)

db = load_db()

@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.from_user.id)
    if user_id not in db:
        db[user_id] = {"name": None, "age": None, "money": 5000 , "state": "awaiting_name"}
        save_db(db)

    KeyboardReply = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)

    helpbutton = telebot.types.KeyboardButton("Инструкция по пользованию ботом")
    infobutton = telebot.types.KeyboardButton("Информация о боте")
    aboutbutton = telebot.types.KeyboardButton("Возврат средств")
    slotMachineButton =  telebot.types.KeyboardButton("Казино")
    leadersButton = telebot.types.KeyboardButton("Таблица лидеров")

    KeyboardReply.add(helpbutton, infobutton, aboutbutton, slotMachineButton, leadersButton)
    bot.send_message(message.chat.id, "Добро пожаловать в DRUID SHOP Как вас зовут? ", reply_markup=KeyboardReply)


@bot.message_handler(commands=['info'])
def info(message):

    bot.send_message(message.chat.id, "Информация о боте")

@bot.message_handler(content_types=['text'])
def text_event(message):
    user_id = str(message.from_user.id)
    if "awaiting_name" == db.get(user_id, {}).get("state"):
        name = message.text.strip()
        db[user_id]["name"] = message.text
        save_db(db)
        db[user_id]["state"] = None
        bot.send_message(message.chat.id,f"Пряитно познакомиться,{name}")
        start(message)
        return

        db[user_id]["money"] = 10000


    if message.text == "Инструкция по пользованию ботом":
        pass
    elif message.text == "Как меня зовут?":
        user_name = db[user_id]["name"]
        bot.send_message(message.chat.id, f"Тебя зовут {user_name}")
    elif message.text == "Таблица лидеров":
        leaders = sorted(
            db.items(),
            key=lambda item:item[1]["money"],
            reverse=True
        )
        top5 = leaders[:5]
        text = "ТОП-5 по деньгам:\n\n"

        for position, (user_id, user_data) in enumerate(top5, start=1):
            text += f"{position}. {user_data['name']} - {user_data['money']}"

        bot.send_message(message.chat.id, text)
    elif message.text == "Казино":
        if db[user_id]["money"] >= 1000:
            value = bot.send_dice(message.chat.id,message.chat.id , emoji='🎰').dice.value

            if value in (1,22,43):
                bot.send_message(message.chat.id, "Победа!Ты выиграл 5000.твой баланс:", {db[user_id]["money"]})
                db[user_id]["money"] += 5000
            elif value in (16,32,48):
                bot.send_message(message.chat.id, "Победа!Ты выиграл 2000.твой баланс:", {db[user_id]["money"]})
                db[user_id]["money"] += 2000
            elif value == 64:
                bot.send_message(message.chat.id, "Джекпот!Ты выиграл 10000.твой баланс:", {db[user_id]["money"]})
                db[user_id]["money"] += 10000
            else:
                db[user_id]["money"] -= 1000
                bot.send_message(message.chat.id,f"Почти! вы проиграли 1000. ваш баланс:", {db[user_id]["money"]})
        else:
            bot.send_message(message.chat.id, f"не достаточно средств должно быть минимум 1000 ваш баланс:", {db[user_id]["money"]})


    elif message.text == "игра в кубик":
        inlineKeyboard = telebot.types.InlineKeyboardMarkup(row_width=3)

        btn1 = telebot.types.InlineKeyboardButton('1',callback_data='1')
        btn2 = telebot.types.InlineKeyboardButton('2', callback_data='2')
        btn3 = telebot.types.InlineKeyboardButton('3', callback_data='3')
        btn4 = telebot.types.InlineKeyboardButton('4', callback_data='4')
        btn5 = telebot.types.InlineKeyboardButton('5', callback_data='5')
        btn6 = telebot.types.InlineKeyboardButton('6', callback_data='6')

        inlineKeyboard.add(btn1, btn2, btn3, btn4, btn5, btn6)

        bot.send_message(message.chat.id, "Угадай число на кубике", reply_markup=inlineKeyboard)

    else:
        bot.send_message(message.chat.id,message.chat.id,message.text)

@bot.callback_query_handler(func=lambda call: call.data in ('1', '2', '3', '4', '5', '6'))
def dice_callback(call):
    value = bot.send_dice(call.message.chat.id, emoji="🎲").dice.value
    if str(value) == call.data:
        bot.send_message(call.message.chat.id, "Ты угадал!")
    else:
        bot.send_message(call.message.chat.id, "Попробуй еще раз")


@bot.message_handler(commands=['back'])
def back(message):
    bot.send_message(message.chat.id, "Возврат средств" )


@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, "Возврат средств" )

@bot.message_handler(content_types=['text'])
def text_event(message):
    bot.send_message(message.chat.id,"В честь открытия магазина скидка 15% на все товары!" )

if __name__ == '__main__':
    server_url = os.getenv("RENDER_EXTERNAL_URL")
    if server_url and API_TOKEN:
        webhook_url = f"{server_url.rstrip('/')}/{API_TOKEN}"

        try:
            r = requests.get(f"https://api.telegram.org/bot{API_TOKEN}/setWebhook",
                             params={"url": webhook_url}, timeout=10)
            logging.info(f"Вебух установлен: {r.text}")
        except Exception:
            logging.exception("Ошибка при установке webhook")

        port = int(os.getnv("port", 10000))
        logging.info(f"Запуск на порте{port}")
        app.run(host='0.0.0.0',port = port)
    else:
        logging.info("Запук бота в режиме pooling")
        bot.remove_webhook()
        bot.infinity_polling(timeout=60)