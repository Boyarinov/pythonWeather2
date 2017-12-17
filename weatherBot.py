#!/usr/bin/env python

import requests
import json
from geopy.geocoders import Nominatim


token = '447876310:AAFtw18lF85T87_NT2_QYNfwHqRjo1nkUIY'
URL = 'https://api.telegram.org/bot' + token + '/'
global last_update
last_update = 0
global up_id
up_id = 0

def get_update():
    url = URL+'getupdates?offset={}'.format(up_id)
    d = requests.get(url)
    return d.json()

def get_message():
    data = get_update()
    last_object = data['result'][-1]
    update_id = last_object['update_id']

    global last_update
    if last_update != update_id:
        last_update = update_id
        global up_id
        up_id = update_id
        try:
            chat_id = last_object['message']['chat']['id']
            message_id=last_object['message']['message_id']
            first_name=last_object['message']['from']['first_name']
            if(last_object['message'].get('photo')!=None):
                text=last_object['message']['photo'][-1]['file_id']
            elif(last_object['message'].get('location')!=None):
                text = last_object['message']['location']
            elif (last_object['message'].get('text')==None):
                text = 'sticker'
            else:
                text = last_object['message']['text']
        except KeyError:
            chat_id = last_object['callback_query']['message']['chat']['id']
            message_id = last_object['callback_query']['message']['message_id']
            text = last_object['callback_query']['data']
            first_name=last_object['callback_query']['message']['from']['first_name']
        message = {'chat_id':chat_id,'text':text,'first_name':first_name,'id':message_id}
        return message

    return None

def send_message(chat_id,text,parse_mode=None,reply_id=None,reply_markup=None):
        url = URL+'sendmessage?chat_id={}&text={}'.format(chat_id,text)
        if(parse_mode !=None):
            url=url+'&parse_mode={}'.format(parse_mode)
        if(reply_id!=None):
            url=url+"&reply_to_message_id={}".format(reply_id)
        if(reply_markup!=None):
            url = url+"&reply_markup={}".format(reply_markup)
        d = requests.get(url).json()
        return d['result']['message_id']

def getWeather(latitude,longitude):
    TodayWeather = []
    AppID = 'cb2a7588'
    KEY = 'fae5651c6413bda3d7db0830ff6f3901'
    Weather_URL= 'http://api.weatherunlocked.com/api/forecast/{},{}?app_id={}&app_key={}'.format(latitude,longitude,AppID,KEY)
##    0 = 2 1 = 5 2 = 8 3 = 11 4 = 14 5 = 17 6 = 20 7 = 23
    for j in range(1,3):
        today = requests.get(Weather_URL).json()['Days'][j]['Timeframes']
        for i in range(2,7,2):
            d = today[i]
            temp_c = d['temp_c']
            time = str(int(d['time']/100))+':00'
            date = d['date']
            info = {'temp':temp_c,'time':time,'date':date}
            TodayWeather.append(info)
    return TodayWeather

def buttonReply():
        button = [[{'text':'🌍 Отправить своё местоположение','request_location':True}]]
        keyboard = {'keyboard':button,'resize_keyboard':True,'one_time_keyboard':False}
        reply = json.dumps(keyboard)
        return reply

def main():
    while(True):
        d = get_message()
        if d!=None:
            chat_id=d['chat_id']
            if (type(d['text'])==dict):
                POX = []
                answer = str(d['text']['latitude'])
                POX.append(d['text']['latitude'])
                POX.append(d['text']['longitude'])
                send_message(chat_id,'Идет получение данных...')
                geolocator = Nominatim()
                location = geolocator.reverse('{},{}'.format(POX[0],POX[1]))
                weather = getWeather(POX[0],POX[1])
                text = 'Погода для локации: "{}"'.format(location.address)
                for i in range(0,6):
                    text +='\n\n📆Дата:\n{} {}'.format(weather[i]['date'],weather[i]['time'])+'\n🌡Температура: {}°\n'.format(weather[i]['temp'])
                send_message(chat_id,text)
                continue
            answer = d['text'].upper()
            if (answer=="/START"):
                url = 'https://vk.com/id445159253'
                button = {'text':'Автор','url':url}
                buttons = [[button]]
                keyboard = {'inline_keyboard':buttons}
                reply = json.dumps(keyboard)
                send_message(chat_id,'Здравствуй, друг.\nБот выдает вам задания из КИМ-ов, которые были на ЕГЭ в прошлом году.\nСложность заданий вы можете выбрать сами.',
                    reply_markup=reply)
                reply = buttonReply()
                send_message(chat_id,"Отправте боту геолокацию того места, в котором вы хотите узнать погоду.",reply_markup = reply)



if __name__=='__main__':
            main()
