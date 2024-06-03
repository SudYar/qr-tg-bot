from interface import update_message, count_sum
# import os
import config # - указаны url и токены
import telebot
from telebot.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
import json
import cv2
import requests
import numpy as np
import pandas as pd



# bot = telebot.TeleBot(os.environ.get('BOT_TOKEN'))
# token = os.environ.get('CHEK_TOKEN')
# url = os.environ.get('CHEK_URL')
bot = telebot.TeleBot(config.TG_token)
bot.remove_webhook() # для локального запуска
token = config.proverkacheka_token
url = config.proverkacheka_url # https://proverkacheka.com/api/v1/check/get


# --------------------- bot ---------------------
@bot.message_handler(commands=['help', 'start'])
def say_hello(message):
    bot.send_message(message.chat.id, 'Привет, я запущен локально')


@bot.message_handler(func=lambda message: True, content_types=["photo"])
def scan_qr_code(message):
    file_path = bot.get_file(message.photo[-1].file_id).file_path
    file = bot.download_file(file_path)
    result_code, has_qr = scanner_cv2(file)
    print("cv2 расшифровал: ", result_code, " qr-код найден: ", has_qr)
    flag = True
    if result_code == '':
        if has_qr:
            try:
                df = proverkacheka_file(file)
            except Exception:
                result, flag = "proverkacheka не отвечает. Попробуйте чуть позже", False
        else:
            result, flag = "Не получилось найти qr-код на снимке", False
    else:
        try:
            df = proverkacheka(result_code)
        except Exception:
            result, flag = "QR-код перевернут или не для nalog.ru", False
    markup = InlineKeyboardMarkup()
    if flag:
        for i in range(len(df)):
            markup.add(InlineKeyboardButton(text=f'{i+1}. Выбрать', callback_data='{{"method": "{0}", "type": "{1}", "number": {2}}}'.format('choice', 'plus', i+1)))
        markup.add(InlineKeyboardButton(text=f'Просуммировать', callback_data='{{"method": "{0}"}}'.format('summ')))
        result = create_message(df)
    bot.send_message(message.chat.id, result, parse_mode='markdown', reply_markup = markup, protect_content=True)


def scanner_cv2(name_file: bytes):
    nparr = np.frombuffer(name_file, np.uint8) 
    image = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)
    # инициализируем детектор QRCode cv2
    detector = cv2.QRCodeDetector()
    # обнаружить и декодировать
    data, bbox, straight_qrcode = detector.detectAndDecode(image)
    f = (bbox is not None)
    return data, f

def proverkacheka(qrraw: str):
    data={'token':token,'qrraw': qrraw}
    r = requests.post(url, data=data)
    data = json.loads(r.text)
    df = pd.json_normalize(data['data']['json']['items'])
    df['price'] = df['price'].apply(lambda x: x/100.0)
    return df[['name', 'price', 'quantity']]

def proverkacheka_file(file: bytes):
    data={'token':token}
    files = {'qrfile': file}
    r = requests.post(url, data=data, files=files)
    data = json.loads(r.text)
    df = pd.json_normalize(data['data']['json']['items'])
    df['price'] = df['price'].apply(lambda x: x/100.0)
    return df[['name', 'price', 'quantity']]

@bot.message_handler(commands=['qr'])
def say_welcome(message):
    bot.send_message(message.chat.id,
                     'Пожалуйста, вместе с командой отправьте ещё фотографию необходимого qr-кода для nalog.ru')


@bot.message_handler(commands=['test'])
def test(message):
    markup = InlineKeyboardMarkup()
    for i in range(3):
        markup.add(InlineKeyboardButton(text=f'{i+1}. Выбрать', callback_data='{{"method": "{0}", "type": "{1}", "number": {2}}}'.format('choice', 'plus', i+1)))
    result = '1. Название: Блинчик с сыром и ветчиной, Цена: 95.35 р., Количество: 3\nВыбрали: , Всего: 0\n2. Название: Борщ с беконом, Цена: 145.88 р., Количество: 1\nВыбрали: , Всего: 0\n3. Название: Блин "Цезарь" с кетчупом, Цена: 212.77 р., Количество: 1\nВыбрали: , Всего: 0'
    bot.send_message(message.chat.id, result, parse_mode='markdown', reply_markup = markup)

@bot.message_handler(func=lambda message: True)
def echo(message):
    bot.send_message(message.chat.id, 'Seems wrong. Use /help to discover more')

def create_message(df):
    title = "Список продуктов из чека:\n"
    df['concat'] = df.apply(lambda row: f"{row.name + 1}. Название: {row['name']}, Цена: *{row['price']}* р., Количество: *{row['quantity']}*", axis = 1)
    text = "\nВыбрали: , Всего: 0\n".join(df['concat'].tolist())
    text += "\nВыбрали: , Всего: 0"
    title += text
    return title

# Обработка нажатий inline-кнопок
@bot.callback_query_handler(func=lambda call:True)
def callback_query(call):
    req = call.data.split('_')
    json_string = json.loads(req[0])
    method = json_string['method']
    if method == 'choice':
        typ = json_string['type']
        number = json_string['number']
        update_message(call, number, call.from_user.username, call.from_user.first_name, typ == "plus")
    if method == 'summ':
        count_sum(call)


# ---------------- local testing ----------------
if __name__ == '__main__':
    bot.infinity_polling()
