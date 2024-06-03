
import telebot
from telebot.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from collections import defaultdict
import re

# ---------- get bot -------------------
# bot = telebot.TeleBot(os.environ.get('BOT_TOKEN'))
bot = telebot.TeleBot('7196565532:AAHxLmUKNjHn7GHwvRJRrXoHhsf3dWxh0OA')


# ---------- methods -----------------------

def update_message(call, num, username, first_name, plus: bool):
    markup = InlineKeyboardMarkup()
    lines = re.split(r'\n', call.message.text)
    couples = [(lines[i], lines[i+1]) for i in range(1, len(lines), 2)]
    have_error = False
    error_message = ''
    newLines = []
    for i in range(len(couples)):
        product_couple = couples[i]
        n = i + 1
        quantity_match = re.search(r"Количество: (\d+)", product_couple[0])
        taken = re.search(r"Всего: (\d+)", product_couple[1])
        if not taken or not quantity_match:
            bot.answer_callback_query(call.id, text=f"У продукта {n} битый формат")
            continue
        quantity = int(quantity_match.group(1))
        count_taken = int(taken.group(1))
        # Если это не целевая строка, то текст не меняется, а кнопки формируются в конце
        if (n != num):
            newLines.append(f"{product_couple[0]}\n{product_couple[1]}")
        # Подсчет людей для "Выбрали"
        else:
            # name_match = re.search(r"Название: (.+?),", product_couple[0])
            # price_match = re.search(r"Цена: (\d+\.\d+) р.,", product_couple[0])
            users_matches = re.findall(r"@(\w+) \((\d+)\)", product_couple[1].replace("Выбрали: ", ""))
            users_without_at = re.findall(r"(?<!@|\w)(\w+) \((\d+)\)", product_couple[1].replace("Выбрали: ", ""))
            
            # if name_match and price_match and quantity_match and taken:
               
                # name = name_match.group(1)
                # price = float(price_match.group(1))
            users = users_matches
            users_withous_username = users_without_at
            # Закоммичено, чтобы делить один продукт на несколько человек
            # if ((count_taken == quantity) and plus):
            #     error_message = f'Уже максимальное число, {count_taken} , {product_couple[0], {n}, {num} }'
            #     have_error = True
            # Аналогично для минимального
            if ((count_taken == '0') and not plus):
                error_message = f"{first_name} и так не был отмечен у продукта №{n}"
                have_error = True
            # Если добавляем продукт
            if plus:
                count_taken += 1
                # Если есть username
                if username is not None:
                    # Перебираем все username. Если есть, то добавим к нему число, если нет то добавим в лист
                    for i, user_match in enumerate(users):
                        if user_match[0] == username:
                            # Создание нового кортежа с обновленным количеством
                            new_couple = (user_match[0], int(user_match[1]) + 1)
                            # Замена старого кортежа новым
                            users[i] = new_couple
                            break
                    else:
                        # Если пользователь не найден, добавляем его в список
                        new_couple = (username, 1)
                        users.append(new_couple)
                else:
                    # Аналогично, но без логинов
                    for i, user_match in enumerate(users_withous_username):
                        if user_match[0] == first_name:
                            # Создание нового кортежа с обновленным количеством
                            new_couple = (user_match[0], int(user_match[1]) + 1)
                            # Замена старого кортежа новым
                            users_withous_username[i] = new_couple
                            break
                    else:
                        # Если пользователь не найден, добавляем его в список
                        new_couple = (first_name, 1)
                        users_withous_username.append(new_couple)

            # Теперь если удаляем
            else:
                count_taken -= 1
                if username is not None:
                    # Перебираем все username. Если есть, то убавим у него число, если нет то нужен flag_error
                    for i, user_match in enumerate(users):
                        if user_match[0] == username:
                            if user_match[1] == '1':
                                users.pop(i)
                            else:
                                # Создание нового кортежа с обновленным количеством
                                new_couple = (user_match[0], int(user_match[1]) - 1)
                                # Замена старого кортежа новым
                                users[i] = new_couple
                            break
                    else:
                        # Если пользователь не найден, значит он зря нажал на кнопку
                        have_error = True
                        error_message = f"{username} и так не был отмечен у продукта №{n}"
                else:
                    # Аналогично, но без логинов
                    for i, user_match in enumerate(users_withous_username):
                        if user_match[0] == first_name:
                            if user_match[1] == '1':
                                users_withous_username.pop(i)
                            else:
                                # Создание нового кортежа с обновленным количеством
                                new_couple = (user_match[0], int(user_match[1]) - 1)
                                # Замена старого кортежа новым
                                users_withous_username[i] = new_couple
                            break
                    else:
                         # Если пользователь не найден, значит он зря нажал на кнопку
                        have_error = True
                        error_message = f"{first_name} и так не был отмечен у продукта №{n}"
            # Ужасная проверка на пользователей закончилась
            if have_error:
                bot.answer_callback_query(call.id, text=error_message)
                break
            else:
                # Формирование строки для пользователей с символом @
                users_with_at_string = ", ".join([f"@{user[0]} ({user[1]})" for user in users])

                # Формирование строки для пользователей без символа @
                users_without_at_string = ", ".join([f"{user[0]} ({user[1]})" for user in users_withous_username])

                # Сбор итоговой строки
                users_string = f"Выбрали: {users_with_at_string}, {users_without_at_string}, Всего: {count_taken}"
                users_string = users_string.replace("Выбрали: , ", "Выбрали: ").replace(", , ", ", ").rstrip(", ")
                newLines.append(f"{product_couple[0]}\n{users_string}")
        # Теперь сами кнопки. Три случая - count_taken = 0, 0<count_taken<quantity, count_taken=quantity
        if (count_taken == 0):
            markup.add(InlineKeyboardButton(text=f'{n}. Выбрать', callback_data='{{"method": "{0}", "type": "{1}", "number": {2}}}'.format('choice', 'plus', n)))
        # elif (count_taken > 0 and count_taken < quantity):
        else:
            markup.add(InlineKeyboardButton(text=f'{n}. Выбрать', callback_data='{{"method": "{0}", "type": "{1}", "number": {2}}}'.format('choice', 'plus', n)),
                InlineKeyboardButton(text=f'Убрать', callback_data='{{"method": "{0}", "type": "{1}", "number": {2}}}'.format('choice', 'minus', n)))
        # else:
        #     markup.add(InlineKeyboardButton(text=f'{n}. Убрать', callback_data='{{"method": "{0}", "type": "{1}", "number": {2}}}'.format('choice', 'minus', n)))
    markup.add(InlineKeyboardButton(text=f'Просуммировать', callback_data='{{"method": "{0}"}}'.format('summ')))
    if not have_error:
        title = "Список продуктов из чека:\n"
        newText = '\n'.join(newLines)
        title += newText
        bot.edit_message_text(title, reply_markup = markup, chat_id=call.message.chat.id, message_id=call.message.message_id, entities=call.message.entities)
            
def count_sum(call):
    pattern = re.compile(
    r"Название:\s*(.*?),\s*Цена:\s*(\d+\.\d+)\s*р\.,\s*Количество:\s*(\d+)\.?\d*\s*"
    r"Выбрали:\s*(.*?),\s*Всего:\s*(\d+)"
    )

    # Словарь для хранения сумм, которые должны пользователи
    user_totals = defaultdict(float)

    # Поиск всех совпадений в тексте
    matches = pattern.findall(call.message.text)

    for match in matches:
        name = match[0]
        price = float(match[1])
        quantity = float(match[2])
        selected_users = match[3]
        total_selected = int(match[4])

        # Извлекаем пользователей и их количество
        user_pattern = re.compile(r"(@?\w+)\s*\((\d+)\)")
        users = user_pattern.findall(selected_users)

        # Обновляем суммы для каждого пользователя
        for user in users:
            username = user[0]
            user_count = int(user[1])
            user_totals[username] += (price * quantity) * (user_count / max(quantity, total_selected))
    result = ''
    # Вывод суммы для каждого пользователя
    for user, total in user_totals.items():
        result += f"{user} должен {total:.2f} р.\n"
    if result == '':
        result = 'Никто ещё не отметился'
    bot.reply_to(call.message, result)



#  500р шт 2
#  отметились 2 я 1 он
#  Нужно чтобы у меня было 500 * 2/3 * 2

# ckexfq 500Р 2 шт
# Я отметил 1 из 2
# Нужно чтобы было 500 * 1/2 * 2
# 