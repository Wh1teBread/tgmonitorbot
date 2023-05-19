import array
from sys import exception
import time
import threading
import requests
import json

import telebot
from telebot import types
bot = telebot.TeleBot('5796886633:AAHGvSj3jZzcReDSKOkntU19lRPhaPoIZAo')

@bot.message_handler(commands=['start'])
def start(message):
    mode = ""

    chatToDatabase(message.chat.id)

    
    bot.send_message(message.chat.id, text="👁️ Вас приветствует бот для мониторинга состояния страниц!\n\n" 
                     +"🔽 Воспользуйтесь меню, чтобы добавить/удалить страницу для мониторинга или включить/выключить мониторинг.\n\n" 
                     +"‼️ Недоступные страницы могут затормаживать работу бота, поэтому уведомления могут приходить с задержкой.\n\n" 
                     +"⚠️ Чтобы вернуться к меню, напишите команду /start.", reply_markup=mainMenuMarkup(message.chat.id))
    
def chatToDatabase(id):
    json_out = json.load(open('requestsdata.json', encoding='utf-8'))

    for i in json_out:
        if i['chatid'] == id:
            #bot.send_message(id, text="⚠️ Вы уже в базе")
            return
        
    user = { "chatid" : id, "links" : [], "delay" : 10, "isWorking" : False, "mode" : ""}
    json_in = json.load(open('requestsdata.json'))
    json_in.append(user)
    with open('requestsdata.json', 'w', encoding='utf-8') as fh:
            json.dump(json_in, fh, indent=4, ensure_ascii=False)    

def chatKey(id):
    key = 0
    json_out = json.load(open('requestsdata.json', encoding='utf-8'))
    for i in json_out:
        if i['chatid'] == id: 
            return key
        else: key += 1

def changeValue(id, name, value):
    key = chatKey(id)

    with open("requestsdata.json", "r", encoding='utf-8') as file:
        data = json.load(file)
    
    data[key][name] = value

    with open('requestsdata.json', 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False) 

def getValue(id, name):
    key = chatKey(id)

    with open("requestsdata.json", "r", encoding='utf-8') as file:
        data = json.load(file)
    
    return data[key][name]

def addLink(id, link):
    key = chatKey(id)

    with open("requestsdata.json", "r", encoding='utf-8') as file:
        data = json.load(file)
    
    arr = data[key]["links"]
    print(arr)
    arr.append(link)
    print(arr)
    changeValue(id, "links", arr)

def deleteLink(id, link):
    key = chatKey(id)

    with open("requestsdata.json", "r", encoding='utf-8') as file:
        data = json.load(file)
    
    data[key]["links"].remove(link)

    with open('requestsdata.json', 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

@bot.message_handler(content_types=['text'])
def actions(message):
    
    if message.text == "Запустить ✅":
        mode = ""
        changeValue(message.chat.id, "mode", "")
        if getValue(message.chat.id, "isWorking") == True:
            bot.send_message(message.chat.id, text="⚠️ Мониторинг уже работает!")
        else:
            if getValue(message.chat.id, "links"):
                changeValue(message.chat.id, "isWorking", True)
                bot.send_message(message.chat.id, text="✅ Мониторинг запущен!", reply_markup=mainMenuMarkup(message.chat.id))
                t1 = threading.Thread(target = thread1, args = (message,)).start()
                print("%s %s (%s) запустил(-а) мониторинг" % (message.from_user.first_name, message.from_user.last_name, message.from_user.username))
            else:
                bot.send_message(message.chat.id, text="⚠️ Список сайтов пуст!\n\n🔽 Воспользуйтесь меню, чтобы добавить новую страницу для мониторинга.", reply_markup=mainMenuMarkup(message.chat.id))

    elif message.text == "Остановить ❌":
        changeValue(message.chat.id, "mode", "")
        if getValue(message.chat.id, "isWorking") == True:
            changeValue(message.chat.id, "isWorking", False)
            bot.send_message(message.chat.id, text="❌ Мониторинг остановлен!", reply_markup=mainMenuMarkup(message.chat.id))
            print("%s %s (%s) остановил(-а) мониторинг" % (message.from_user.first_name, message.from_user.last_name, message.from_user.username))
        else:
            bot.send_message(message.chat.id, text="⚠️ Мониторинг еще не запущен!")
        
    elif message.text == "Добавить страницу ➕":
        changeValue(message.chat.id, "mode", "adding")
        bot.send_message(message.chat.id, text="👁️ Отправьте ссылку на страницу, которую нужно добавить в список мониторинга. \n\n"
                        +"⚠️ Ссылка может как начинаться с https://, так и нет. Примеры ссылок: \n▫️ https://example.com\n▫️ example.com", reply_markup=returnMarkup())

    elif message.text == "Удалить страницу ➖":
        changeValue(message.chat.id, "mode", "deleting")
        bot.send_message(message.chat.id, text="⛔ Отправьте ссылку на страницу, которую нужно убрать из списка мониторинга.", reply_markup=returnMarkup())

    elif message.text == "Изменить период проверки 🕖":
        changeValue(message.chat.id, "mode", "timechanging")
        bot.send_message(message.chat.id, text="🕧 Отправьте число секунд, через которое будет производиться проверка страниц.\n\n⚠️ Время не должно быть меньше 5 секунд!", reply_markup=returnMarkup())

    elif message.text == "↩️ Возврат":
        changeValue(message.chat.id, "mode", "")
        start(message)

    elif message.text == "Список страниц 👁️":
        changeValue(message.chat.id, "mode", "")
        
        websites = getValue(message.chat.id, "links")
        stroke = "👁️ Ваш список мониторящихся страниц: \n\n"
        for i in websites:
            stroke = stroke + "▫️ " + i + "\n"
        stroke += "\n🔽 Вы можете добавить/удалить страницы с помощью меню."
        bot.send_message(message.chat.id, text=stroke, reply_markup=mainMenuMarkup(message.chat.id))

    else:
        if getValue(message.chat.id, "mode") == "adding":
            try: 
                msg = message.text
                msg = msg if msg.startswith('https') else ('https://' + msg)
                r = requests.get(msg)
                if msg in getValue(message.chat.id, "links"):
                    bot.send_message(message.chat.id, text="⚠️ Такая ссылка уже имеется!", reply_markup=returnMarkup())
                else:
                    addLink(message.chat.id, msg)
                    bot.send_message(message.chat.id, text="✅ Страница добавлена в список мониторинга!\n\n🔽 Можете добавить еще ссылку или вернуться в меню.", reply_markup=returnMarkup())

            except requests.ConnectionError:
                bot.send_message(message.chat.id, text="✅ Страница сейчас недоступна, но мы добавили ее в список мониторинга.\n\n🔽 Можете добавить еще ссылку или вернуться в меню.", reply_markup=returnMarkup())
                addLink(message.chat.id, msg)

            except requests.RequestException:
                bot.send_message(message.chat.id, text="⚠️ Пожалуйста, введите ссылку, а не текст!", reply_markup=returnMarkup())

        elif getValue(message.chat.id, "mode") == "deleting":
            msg = message.text
            msg = msg if msg.startswith('https') else ('https://' + msg)
            if msg in getValue(message.chat.id, "links"):
                deleteLink(message.chat.id, msg)
                bot.send_message(message.chat.id, text="✅ Ссылка успешно удалена!\n\n🔽 Можете добавить еще ссылку или вернуться в меню.", reply_markup=returnMarkup())
            else:
                bot.send_message(message.chat.id, text="⚠️ Такой ссылки в списке нет!", reply_markup=returnMarkup())

        elif getValue(message.chat.id, "mode") == "timechanging":
            if message.text.isnumeric():
                if int(message.text) >= 5:
                    changeValue(message.chat.id, "delay", int(message.text))
                    bot.send_message(message.chat.id, text="✅ Время успешно задано!")
                    start(message)
                else: 
                    bot.send_message(message.chat.id, text="⚠️ Время не должно быть меньше 5 секунд!")
            else:
                bot.send_message(message.chat.id, text="⚠️ Введите число секунд, а не текст!", reply_markup=returnMarkup())
        
def mainMenuMarkup(id):
    mainMenu = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if getValue(id, "isWorking") == False:
        btn1 = types.KeyboardButton("Запустить ✅")
    else:
        btn1 = types.KeyboardButton("Остановить ❌")
    btn2 = types.KeyboardButton("Добавить страницу ➕")
    btn3 = types.KeyboardButton("Удалить страницу ➖")
    btn4 = types.KeyboardButton("Изменить период проверки 🕖")
    btn5 = types.KeyboardButton("Список страниц 👁️")
    mainMenu.row(btn1)
    mainMenu.row(btn2, btn3)
    mainMenu.row(btn4, btn5)
    return mainMenu

def returnMarkup():
    returnMenu = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("↩️ Возврат")
    returnMenu.row(btn1)
    return returnMenu

def thread1(message):
    websites = getValue(message.chat.id, "links")
    while True:
        if getValue(message.chat.id, "isWorking") == False: return
        pinging(message)
        time.sleep(getValue(message.chat.id, "delay"))

def pinging(message):

    websites = getValue(message.chat.id, "links")
    delay = getValue(message.chat.id, "delay")

    web_ping = "Результаты мониторинга (%s секунд): \n" % (delay)
    for w in websites:
        status = ""
        code = ""
        try:
            r = requests.get(w) 

            if r.status_code >= 300 and r.status_code < 400:
                code = r.status_code
                status = "🟡 Произошло перенаправление"

            elif r.status_code >= 400 and r.status_code < 500:
                code = r.status_code
                status = "🟡 Ошибка клиента"

            elif r.status_code >= 500:
                code = r.status_code
                status = "🟡 Ошибка сервера"

            elif r.status_code == 200:
                code = r.status_code
                status = "🟢 Страница доступна"
            
        except requests.ConnectionError:
            code = "-"
            status = "🔴 Ошибка соединения!"

        except requests.RequestException:
            code = "-"
            status = "Неверный ввод"
    
        web_ping = "%s\nАдрес: %s \nКод: %s \nСтатус: %s\n" % (web_ping, w, code, status)

    if getValue(message.chat.id, "isWorking"):
        bot.send_message(message.chat.id, text=web_ping)

@bot.message_handler(content_types=['sticker'])
def turnOff(message):
    if message.chat.id != 432061959: return
    
    with open("requestsdata.json", "r", encoding='utf-8') as file:
        data = json.load(file)
    
    for i in data:
        i["isWorking"] = False

    with open('requestsdata.json', 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

bot.polling(none_stop=True, interval=0)

