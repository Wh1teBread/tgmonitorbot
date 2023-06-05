from bs4 import BeautifulSoup
import requests
import telebot
from telebot import types
bot = telebot.TeleBot('5796886633:AAHGvSj3jZzcReDSKOkntU19lRPhaPoIZAo')

@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.id != 432061959: return
    page = requests.get("https://arsenaltula.ru/season/calendar-2/")

    soup = BeautifulSoup(page.text, "html.parser")
    upcoming_blocks = soup.findAll('a', class_='block')

    notification = "🔼Предстоящие матчи:\n\n"

    if upcoming_blocks:
        upcoming_matches = []
    
        for data in upcoming_blocks:
            upcoming = {'date': '', 'teams': [], 'place':''}

            #дата
            upcoming['date'] = data.find('div', class_='block__title').text
            upcoming['date'] = upcoming['date'].replace('Вторая лига', '')

            #команды
            teams = data.findAll('h4', class_='team__name')
            for i in teams:
                tmp = i.text.replace('                                           ', '')
                upcoming['teams'].append(tmp)
        
            #место
            upcoming['place'] = data.find('div', class_="block__place").text
        

            upcoming_matches.append(upcoming)
        for i in upcoming_matches:
            notification += "%s ⚔️ %s\n🕖 Время проведения: %s🏟️ Место проведения: %s\n\n" % (i['teams'][0], i['teams'][1], i['date'], i['place'])
    
    else:
        notification += "❌ Предстоящих матчей нет!\n\n"

    bot.send_message(message.chat.id, text=notification)
    bot.send_message(message.chat.id, text="🔽Прошедшие матчи:")

    previous_blocks = soup.findAll('div', class_='matchs__item event')

    if previous_blocks:
        previous_matches = []
    
        for data in previous_blocks:
            previous = {'date': '', 'teams': [], 'place':'', 'score':''}

            #дата
            previous['date'] = data.find('div', class_='event__date').text

            #команды
            teams = data.findAll('h4', class_='team__name')
            for i in teams:
                tmp = i.text.replace('                                           ', '')
                previous['teams'].append(tmp)
        
            #место
            previous['place'] = data.find('div', class_="event__place").text

            #cчет
            previous['score'] = data.find('h3', class_="event__score score").text
            previous['score'] = previous['score'].replace('                                               ', '')
            previous['score'] = previous['score'].replace('ЗАВЕРШЁН', '')

            previous_matches.append(previous)

            
        for i in previous_matches:
            msg = "%s ⚔️ %s\n⚠️ Счет: %s\n🕖 Время проведения: %s\n🏟️ Место проведения: %s" % (i['teams'][0], i['teams'][1], i['score'], i['date'], i['place'])
            bot.send_message(message.chat.id, text=msg)

bot.polling(none_stop=True, interval=0)