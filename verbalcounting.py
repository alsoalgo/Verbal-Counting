import requests
import json
import time
from random import randint

TOKEN = "" #tg : @BotFather

proxies = {
  'http': 'http://144.217.225.220:80/',
  'https': 'https://149.56.102.220:3128/',
}

url = "https://api.telegram.org/bot" + TOKEN + "/"
greeting = "I'm verbal counting game bot.\nI'll send you arithmetics examples kind of X%2bY.\nAfter that I'll wait 7 secs for your answer.\nIf you can't answer, you Lose.\nGood luck!"

data = []
score = dict()
answers = dict()

def arithmetics_expression():
    first = str(randint(0, 150))
    second = str(randint(0, 150))
    expression =  first + "%2b" + second
    return expression, int(first) + int(second)

def send_message(text, chat_id):
    r = requests.get(url + "sendMessage?chat_id=" + str(chat_id) + "&text=" + text, proxies=proxies)
    return json.loads(r.text)


def get_updates():
    r = requests.get(url + "getUpdates", proxies=proxies)
    return json.loads(r.text)

def send_and_save(text, chat_id):
    send_message(text, chat_id)
    if 'lose' not in text:
        send = arithmetics_expression()
        ask = send_message(send[0], chat_id)
        answers[chat_id] = [send[1], ask['result']['date']]

def analyse(data):
    message = data['message']
    chat = message['chat']
    chat_id = chat['id']
    text = message['text']
    current_date = message['date']
    if text.strip() in ["/start", "/help"]:
        score[chat_id] = 0
        send_and_save(greeting, chat_id)
    else:
        try:
            answer = answers[chat_id]
            user_answer = int(text)
            if user_answer == answer[0]:
                if answer[1] + 7 > current_date:
                    score[chat_id] += 1
                    send_and_save("Right answer!\nGet next one!", chat_id)
                else:
                    send_and_save("You lose...\nYour score : " + str(score[chat_id]), chat_id)
                    score[chat_id] = 0
            else:
                send_and_save("Wrong answer!\n You lose...\nYour score : " + str(score[chat_id]), chat_id)
                score[chat_id] = 0
        except ValueError:
            send_and_save("That's not number, so, you lose...\nYour score : " + str(score[chat_id]), chat_id)
            score[chat_id] = 0
        except KeyError:
            score[chat_id] = 0
            send_and_save(greeting, chat_id)

data = get_updates()

while True: #Основной цикл работы бота
    new_data = get_updates()
    if data['result'] != new_data['result']:
        for update in new_data['result'][len(data['result']):]:
            analyse(update)
            print(update['message']['text'])
        data = new_data
    time.sleep(0.5)
