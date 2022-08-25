"""
Наблюдаемый вами кусок кода это переобдуманый голосовой помощник ("Ozeta helper" -> "Fula")
Все функции в виде списка можно просмотреть на github-е проекта:
Ссылка - https://github.com/AsrielStory/Fula_AI
Автор - Asriel_Story
"""

# Библиотеки
from vosk import Model, KaldiRecognizer  # STT
from random import choice, randint
from playsound import playsound  # Версия 1.2.2
from num2words import num2words
import sounddevice
import googletrans  # Версия 3.1.0a0
import webbrowser
import pymorphy2
import pyperclip
import requests
import pyaudio
import string
import socket
import pynput
import psutil
import numpy
import torch  # Silero (TTS)
import time
import json
import bs4
import os


# Конфиги Fula
Fula = {
    'name': 'Fula',
    'name_rus': 'фула',
    'version': '0.0.3',
    'author': 'Asriel_Story',
    'web-site': '...',
    'github': 'https://github.com/AsrielStory/Fula_AI',
    'weather_id': 'f76f1c4ed170f79ddea0b7862b53ecae',
}


# Вывод в формате логов
def log_print(key, text):
    print('[' + time.ctime() + ']', "[" + key + "]", text)

# Конфиги для переводчика
translator = googletrans.Translator()

# Конфиги для клавиатуры
keyboard_controller = pynput.keyboard.Controller()

# Изменение падежей
morph = pymorphy2.MorphAnalyzer()

# Основные настройки vosk
model = Model("small_model")  # Есть 2 модели большая и маленькая (model и small_model)
rec = KaldiRecognizer(model, 16000)
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
stream.start_stream()

# Silero config
local_file = 'model.pt'

# Нужно на случай отсутствия нужной Silero модели
if not os.path.isfile(local_file):
    torch.hub.download_url_to_file('https://models.silero.ai/models/tts/ru/v3_1_ru.pt', local_file)

language = 'ru'
model_id = 'v3_1_ru'
sample_rate = 48000
speaker = 'baya'  # Голоса в налиции: aidar, baya, kseniya, xenia, random
put_accent = True
put_yo = True
device = torch.device('cpu')  # Можно использовать или cpu, или gpu (gpu выбрасывает ошибку)
model = torch.package.PackageImporter(local_file).load_pickle("tts_models", "model")
model.to(device)

# Разговорник Silero
def text_to_speak(txt_speak):
    audio = model.apply_tts(text=txt_speak + '..',
                            speaker=speaker,
                            sample_rate=sample_rate,
                            put_accent=put_accent,
                            put_yo=put_yo)
    # Debug
    log_print('Ответ', txt_speak)

    sounddevice.play(audio, sample_rate * 1.05)
    time.sleep((len(audio) / sample_rate) + 0.5)
    sounddevice.stop()

# Обыкновенный макет распознавателя речи vosk (STT)
def speak_to_text():
    while True:
        data = stream.read(4000, exception_on_overflow=False)
        if rec.AcceptWaveform(data) and len(data) > 0:
            answer = json.loads(rec.Result())
            if answer['text']:
                yield answer['text']

# Вторичный STT
def speak_to_text_secondary():
    for txt_answer in speak_to_text():
        if txt_answer != '':
            # Debug
            log_print('Услышанное', txt_answer)
            return txt_answer

# Преобразователь чисел в слова (0 - 60)
int_to_string = (
    'ноль', 'один', 'два', 'три', 'четыре', 'пять', 'шесть', 'семь', 'восемь', 'девять', 'десять',
    'одиннадцать', 'двенадцать', 'тринадцать', 'четырнадцать', 'пятнадцать', 'шестнадцать', 'семнадцать',
    'восемнадцать', 'девятнадцать', 'двадцать', 'двадцать один', 'двадцать два', 'двадцать три',
    'двадцать четыре', 'двадцать пять', 'двадцать шесть', 'двадцать семь', 'двадцать восемь',
    'двадцать девять', 'тридцать', 'тридцать один', 'тридцать два', 'тридцать три', 'тридцать четыре',
    'тридцать пять', 'тридцать шесть', 'тридцать семь', 'тридцать восемь', 'тридцать девять', 'сорок',
    'сорок один', 'сорок два', 'сорок три', 'сорок четыре', 'сорок пять', 'сорок шесть', 'сорок семь',
    'сорок восемь', 'сорок девять', 'пятьдесят', 'пятьдесят один', 'пятьдесят два', 'пятьдесят три',
    'пятьдесят четыре', 'пятьдесят пять', 'пятьдесят шесть', 'пятьдесят семь', 'пятьдесят восемь',
    'пятьдесят девять', 'шестьдесят'
)

# Склонения часов
hours_norm = ("часов", "час", "часа", "часа", "часа", "часов", "часов", "часов", "часов", "часов", "часов", "часов",
              "часов", "часов", "часов", "часов", "часов", "часов", "часов", "часов", "часов", "час", "часа", "часа",
              "часа")

# Перевод английских букв в русские звуки
letters_norm = {
        'A': 'эй', 'B': 'би', 'C': 'си', 'D': 'ди', 'E': 'и', 'F': 'эф', 'G': 'джи', 'H': 'эйч', 'I': 'ай',
        'J': 'джей', 'K': 'кей', 'L': 'эл', 'M': 'эм', 'N': 'эн', 'O': 'оу', 'P': 'пи', 'Q': 'кью', 'R': 'ар',
        'S': 'эс', 'T': 'ти', 'U': 'ю', 'V': 'ви', 'W': 'дабл-ю', 'X': 'экс', 'Y': 'уай', 'Z': 'зи',
    }

# Склонения минут + перевод числа в строку
# Переделать (уменьшить ограничение по минутам)
def minute_norm(num):
    if num == 1:
        return "одна минута"
    elif num == 2:
        return "две минуты"
    elif num == 21:
        return "двадцать одна минута"
    elif num == 22:
        return "двадцать две минуты"
    elif num == 31:
        return "тридцать одна минута"
    elif num == 32:
        return "тридцать две минуты"
    elif num == 41:
        return "сорок одна минута"
    elif num == 42:
        return "сорок две минуты"
    elif num == 51:
        return "пятьдесят одна минута"
    elif num == 52:
        return "пятьдесят две минуты"
    elif num == 3 or num == 4 or num == 23 or num == 24 or num == 33 or num == 34 or num == 43 or num == 44 or num == 53 or num == 54:
        return int_to_string[num] + " минуты"
    else:
        return int_to_string[num] + " минут"

# Склонение градусов + перевод числа в строку
def degree_norm(num):
    if abs(num % 10) == 1 and abs(num) != 11:
        return (int_to_string[num] + ' градус цельсия')
    elif (abs(num) % 10 == 2 or abs(num) % 10 == 3 or abs(num) % 10 == 4) and abs(num) != 12 and abs(num) != 13 and abs(num) != 14:
        return (int_to_string[num] + ' градуса цельсия')
    else:
        return (int_to_string[num] + ' градусов цельсия')

# Склонение скорости в метрах в секунду
def speed_norm(num):
    if num % 10 == 1 and num != 11:
        return (int_to_string[num] + ' метр в секунду')
    elif (num % 10 == 2 or num % 10 == 3 or num % 10 == 4) and num != 12 and num != 13 and num != 14:
        return (int_to_string[num] + ' метра в секунду')
    else:
        return (int_to_string[num] + ' метров в секунду')

# Проверка интернет соединения
def internet_connection(url='www.google.com'):
    try:
        socket.gethostbyaddr(url)
    except socket.gaierror:
        return False
    else:
        return True


# /=======\
# |Команды|
# \=======/

# Время
def w_time(input_text = ''):
    hour = int(time.strftime("%H"))
    minute = int(time.strftime("%M"))
    text = f"{str(int_to_string[hour])} {str(hours_norm[hour])} {str(minute_norm(minute))}"
    text_to_speak(text)

# Будильник ДОБАВИТЬ
def alarm_add(input_text = ''):
    pass

# Будильник УДАЛИТЬ
def alarm_del(input_text = ''):
    pass

# Напоминалка ДОБАВИТЬ
def sticker_add(input_text = ''):
    pass

# Напоминалка УДАЛИТЬ
def sticker_del(input_text = ''):
    pass

# Список дел ПРОЧИТАТЬ
def to_do_list_read(input_text = ''):
    pass

# Список дел ДОБАВИТЬ
def to_do_list_add(input_text = ''):
    pass

# Список дел УДАЛИТЬ
def to_do_list_del(input_text = ''):
    pass

# Генератор паролей (в буфер)
def gen_password(input_text = ''):
    symbols_gen_password = string.ascii_letters + string.digits
    text_to_speak('Какая длинна должна быть у вашего пароля?')
    answ = speak_to_text_secondary()
    if answ in int_to_string:
        num = int_to_string.index(answ)
    else:
        while True:
            text_to_speak('Число должно входить в рамки от трёх до шестидесяти')
            answ = speak_to_text_secondary()
            if answ in int_to_string:
                num = int_to_string.index(answ)
                break
    password = ''
    for i in range(num):
        password += choice(symbols_gen_password)
    pyperclip.copy(password)
    text_to_speak('Я придумала пароль и скопировала его в буфер обмена')

# Поиск в Google
def search_google(input_text = ''):
    if not(internet_connection('www.google.com')):
        random_internet_null = ('Я не обнаружила интернет соединения', 'К сожалению я не смогу этого узнать, так как у меня нет интернет соединения')
        text_to_speak(choice(random_internet_null))
        return -1
    for i in Fula_cmd_key['search_google']:
        if i in input_text:
            key = i
            break
    if input_text == key:
        random_search_null = ('Что вы хотите поискать в гугле?', 'Что вы хотите узнать в гугле?', 'Что вы хотите загуглить?')
        text_to_speak(choice(random_search_null))
        answ = speak_to_text_secondary()
        input_text += ' ' + answ
        if answ == 'отмена':
            random_search_null_back = ('Окей', 'Ладно', 'Хорошо')
            text_to_speak(choice(random_search_null_back))
            return 0
    url_g = 'https://www.google.com/search?q=' + '+'.join(input_text.split()[input_text.split().index(key.split()[-1]) + 1:])
    random_search = ('Секунду', 'Сею секунду', 'Вот', 'Сейчас поищу', 'Секунду сейчас поищу', 'Секундочку сейчас поищу', '')
    text_to_speak(choice(random_search))
    webbrowser.open(url_g)
    log_print('Ссылка', url_g)

# Поиск в Yandex
def search_yandex(input_text = ''):
    if not(internet_connection('www.yandex.com')):
        random_internet_null = ('Я не обнаружила интернет соединения', 'К сожалению я не смогу этого узнать, так как у меня нет интернет соединения')
        text_to_speak(choice(random_internet_null))
        return -1
    for i in Fula_cmd_key['search_yandex']:
        if i in input_text:
            key = i
            break
    if input_text == key:
        random_search_null = ('Что вы хотите поискать в яндексе?', 'Что вы хотите узнать в яндексе?')
        text_to_speak(choice(random_search_null))
        answ = speak_to_text_secondary()
        input_text += ' ' + answ
        if answ == 'отмена':
            random_search_null_back = ('Окей', 'Ладно', 'Хорошо')
            text_to_speak(choice(random_search_null_back))
            return -1
    url_y = 'https://yandex.by/search/?text=' + '+'.join(input_text.split()[input_text.split().index(key.split()[-1]) + 1:])
    random_search = ('Секунду', 'Сею секунду', 'Вот', 'Сейчас поищу', 'Секунду сейчас поищу', 'Секундочку сейчас поищу', '')
    text_to_speak(choice(random_search))
    webbrowser.open(url_y)
    log_print('Ссылка', url_y)

# Погода
def weather(input_text = ''):
    if not(internet_connection()):
        random_internet_null = ('Я не обнаружила интернет соединения', 'К сожалению я не смогу сказать погоду, так как у меня нет интернет соединения', 'Я не смогу рассказать про погоду, так как нету интернет соединения')
        text_to_speak(choice(random_internet_null))
        return -1
    if ('в' in input_text or 'на' in input_text or 'во' in input_text) and not('неделю' in input_text or 'сегодня' in input_text or 'понедельник' in input_text or 'вторник' in input_text or 'среду' in input_text or 'четверг' in input_text or 'пятницу' in input_text or 'суботу' in input_text or 'воскресенье' in input_text) and not(input_text.split().count('во') + input_text.split().count('в') + input_text.split().count('на') == 1 and 'завтра' in input_text):
        if 'в' in input_text.split():
            index_key = 'в'
        elif 'во' in input_text.split():
            index_key = 'во'
        elif 'на' in input_text.split():
            index_key = 'на'
        try:
            geo_clear = input_text.split()[input_text.split().index(index_key) + 1]
            try:
                geo_clear = morph.parse(geo_clear)[0].inflect({'nomn'}).word
            except AttributeError:
                text_to_speak('К сожелению, я не знаю какая погода в том месте, которое вы сказали')
                return -1
        except UnboundLocalError:
            geo_mud = bs4.BeautifulSoup(requests.get('https://yandex.by/internet').text, "html.parser").find_all('div', class_='location-renderer__value')
            for i in geo_mud:
                geo_clear = i.text
            geo_clear = geo_clear.strip().split()[-1]
    else:
        geo_mud = bs4.BeautifulSoup(requests.get('https://yandex.by/internet').text, "html.parser").find_all('div', class_='location-renderer__value')
        for i in geo_mud:
            geo_clear = i.text
        geo_clear = geo_clear.strip().split()[-1]
    if 'завтра' in input_text and not('после' in input_text):
        weather_data = requests.get("https://api.openweathermap.org/data/2.5/forecast", params={'q': geo_clear, 'units': 'metric', 'lang': 'ru', 'appid': Fula['weather_id']}).json()
        if int(weather_data['cod']) == 404:
            text_to_speak('К сожелению, я не знаю какая погода в том месте, которое вы сказали')
            return -1
        text = ''
        pp_geo = morph.parse(geo_clear)[0].inflect({'loct'}).word
        tomorrow_weather = []
        tomorrow_weather_temp = int(-100)
        tomorrow_weather_weather_max = 0
        tomorrow_weather_weather_max_name = ''
        tomorrow_weather_weather_sort = dict()
        i_time = weather_data['list'][0]['dt_txt'].split()[0]
        i_o = True
        for i in weather_data['list']:
            if i_time != i['dt_txt'].split()[0] and i_o:
                i_o = False
                i_time = i['dt_txt'].split()[0]
            elif i_time != i['dt_txt'].split()[0] and not(i_o):
                break
            if i_time == i['dt_txt'].split()[0] and not(i_o):
                tomorrow_weather.append(i)
                if i['main']['temp_max'] > int(tomorrow_weather_temp):
                    tomorrow_weather_temp = int(i['main']['temp_max'])
                tomorrow_weather_weather_sort.setdefault(i['weather'][0]['description'], 0)
                tomorrow_weather_weather_sort[i['weather'][0]['description']] += 1
                if tomorrow_weather_weather_sort[i['weather'][0]['description']] >= tomorrow_weather_weather_max:
                    tomorrow_weather_weather_max = tomorrow_weather_weather_sort[i['weather'][0]['description']]
                    tomorrow_weather_weather_max_name = i['weather'][0]['description']
        random_weather_start = (f'Погода в {pp_geo} на завтра', f'Сейчас я вам расскажу о завтрашней погоде в {pp_geo}', f'Завтра в {pp_geo}')
        text += choice(random_weather_start) + ' . . . '
        random_weather_weather = (f'За окном будет {tomorrow_weather_weather_max_name}', )
        text += choice(random_weather_weather) + ' . . . '
        random_weather_temp = (f'Температура же завтра будет {degree_norm(tomorrow_weather_temp)}', f'Температура же будет {degree_norm(tomorrow_weather_temp)}')
        text += choice(random_weather_temp) + ' . . . '
        text_to_speak(text)
    elif 'завтра' in input_text and input_text.count('после') == 1:
        weather_data = requests.get("https://api.openweathermap.org/data/2.5/forecast", params={'q': geo_clear, 'units': 'metric', 'lang': 'ru', 'appid': Fula['weather_id']}).json()
        if int(weather_data['cod']) == 404:
            text_to_speak('К сожелению, я не знаю какая погода в том месте, которое вы сказали')
            return -1
        text = ''
        pp_geo = morph.parse(geo_clear)[0].inflect({'loct'}).word
        tomorrow_weather = []
        tomorrow_weather_temp = int(-100)
        tomorrow_weather_weather_max = 0
        tomorrow_weather_weather_max_name = ''
        tomorrow_weather_weather_sort = dict()
        i_time = weather_data['list'][0]['dt_txt'].split()[0]
        i_o1 = True
        i_o2 = True
        for i in weather_data['list']:
            if i_time != i['dt_txt'].split()[0] and i_o1 and i_o2:
                i_o1 = False
                i_time = i['dt_txt'].split()[0]
            elif i_time != i['dt_txt'].split()[0] and not(i_o1) and i_o2:
                i_o2 = False
                i_time = i['dt_txt'].split()[0]
            elif i_time != i['dt_txt'].split()[0] and not(i_o1) and not(i_o2):
                break
            if i_time == i['dt_txt'].split()[0] and not(i_o1) and not(i_o2):
                tomorrow_weather.append(i)
                if i['main']['temp_max'] > int(tomorrow_weather_temp):
                    tomorrow_weather_temp = int(i['main']['temp_max'])
                tomorrow_weather_weather_sort.setdefault(i['weather'][0]['description'], 0)
                tomorrow_weather_weather_sort[i['weather'][0]['description']] += 1
                if tomorrow_weather_weather_sort[i['weather'][0]['description']] >= tomorrow_weather_weather_max:
                    tomorrow_weather_weather_max = tomorrow_weather_weather_sort[i['weather'][0]['description']]
                    tomorrow_weather_weather_max_name = i['weather'][0]['description']
        random_weather_start = (f'Погода в {pp_geo} на послезавтра', f'Сейчас я вам расскажу о послезавтрашней погоде в {pp_geo}', f'Послезавтра в {pp_geo}')
        text += choice(random_weather_start) + ' . . . '
        random_weather_weather = (f'За окном будет {tomorrow_weather_weather_max_name}',)
        text += choice(random_weather_weather) + ' . . . '
        random_weather_temp = (f'Температура же послезавтра будет {degree_norm(tomorrow_weather_temp)}', f'Температура же будет {degree_norm(tomorrow_weather_temp)}')
        text += choice(random_weather_temp) + ' . . . '
        text_to_speak(text)
    elif 'завтра' in input_text and input_text.count('после') == 2:
        weather_data = requests.get("https://api.openweathermap.org/data/2.5/forecast", params={'q': geo_clear, 'units': 'metric', 'lang': 'ru', 'appid': Fula['weather_id']}).json()
        if int(weather_data['cod']) == 404:
            text_to_speak('К сожелению, я не знаю какая погода в том месте, которое вы сказали')
            return -1
        text = ''
        pp_geo = morph.parse(geo_clear)[0].inflect({'loct'}).word
        tomorrow_weather = []
        tomorrow_weather_temp = int(-100)
        tomorrow_weather_weather_max = 0
        tomorrow_weather_weather_max_name = ''
        tomorrow_weather_weather_sort = dict()
        i_time = weather_data['list'][0]['dt_txt'].split()[0]
        i_o1 = True
        i_o2 = True
        i_o3 = True
        for i in weather_data['list']:
            if i_time != i['dt_txt'].split()[0] and i_o1 and i_o2 and i_o3:
                i_o1 = False
                i_time = i['dt_txt'].split()[0]
            elif i_time != i['dt_txt'].split()[0] and not(i_o1) and i_o2 and i_o3:
                i_o2 = False
                i_time = i['dt_txt'].split()[0]
            elif i_time != i['dt_txt'].split()[0] and not(i_o1) and not(i_o2) and i_o3:
                i_o3 = False
                i_time = i['dt_txt'].split()[0]
            elif i_time != i['dt_txt'].split()[0] and not(i_o1) and not(i_o2) and not(i_o3):
                break
            if i_time == i['dt_txt'].split()[0] and not(i_o1) and not(i_o2) and not(i_o3):
                tomorrow_weather.append(i)
                if i['main']['temp_max'] > int(tomorrow_weather_temp):
                    tomorrow_weather_temp = int(i['main']['temp_max'])
                tomorrow_weather_weather_sort.setdefault(i['weather'][0]['description'], 0)
                tomorrow_weather_weather_sort[i['weather'][0]['description']] += 1
                if tomorrow_weather_weather_sort[i['weather'][0]['description']] >= tomorrow_weather_weather_max:
                    tomorrow_weather_weather_max = tomorrow_weather_weather_sort[i['weather'][0]['description']]
                    tomorrow_weather_weather_max_name = i['weather'][0]['description']
        random_weather_start = (f'Погода в {pp_geo} на после послезавтра', f'Сейчас я вам расскажу о после послезавтрашней погоде в {pp_geo}', f'После послезавтра в {pp_geo}')
        text += choice(random_weather_start) + ' . . . '
        random_weather_weather = (f'За окном будет {tomorrow_weather_weather_max_name}',)
        text += choice(random_weather_weather) + ' . . . '
        random_weather_temp = (f'Температура же после послезавтра будет {degree_norm(tomorrow_weather_temp)}', f'Температура же будет {degree_norm(tomorrow_weather_temp)}')
        text += choice(random_weather_temp) + ' . . . '
        text_to_speak(text)
    elif 'сейчас' in input_text.split():
        weather_data = requests.get("https://api.openweathermap.org/data/2.5/weather", params={'q': geo_clear, 'units': 'metric', 'lang': 'ru', 'appid': Fula['weather_id']}).json()
        if int(weather_data['cod']) == 404:
            text_to_speak('К сожелению, я не знаю какая погода в том месте, которое вы сказали')
            return -1
        text = ''
        pp_geo = morph.parse(geo_clear)[0].inflect({'loct'}).word
        random_weather_start = (f"Погода в {pp_geo} на сегодня", f"Сейчас я вам расскажу о сегодняшней погоде в {pp_geo}", f"Сегодня в {pp_geo}")
        text += choice(random_weather_start) + ' . '
        if weather_data['weather'][0]['description'] == 'ясно':
            text += f'В {pp_geo} наблюдается ясное небо . '
        elif weather_data['weather'][0]['description'] == 'пасмурно':
            text += f'На улице виднеется пасмурная погода . '
        elif weather_data['weather'][0]['description'] == 'облачно с прояснениями':
            text += f'В {pp_geo} на небе наблюдается облачная с прояснениями погода . '
        elif weather_data['weather'][0]['description'] == 'переменная облачность':
            text += f'На небе наблюдается переменная облачность . '
        elif weather_data['weather'][0]['description'] == 'морось':
            text += f'На улице наблюдается моросящий дождь . '
        elif weather_data['weather'][0]['description'] == 'небольшой дождь':
            text += f'В {pp_geo} наблюдается небольшой дождь . '
        elif weather_data['weather'][0]['description'] == 'небольшой проливной дождь':
            text += f'За окном наблюдается небольшой проливной дождь . '
        elif weather_data['weather'][0]['description'] == 'дождь':
            text += f'За окном наблюдается дождь . '
        elif weather_data['weather'][0]['description'] == 'сильный дождь':
            text += f'В {pp_geo} с неба льёт сильный дождь . '
        else:
            text += f"За окном в {pp_geo} наблюдается {weather_data['weather'][0]['description']} . "
        text += f"Температура же воздуха составляет {degree_norm(int(weather_data['main']['temp']))} . "
        if weather_data['wind']['deg'] == 0 or weather_data['wind']['deg'] == 360:
            text += f"Ветер сегодня западный со скоростью {speed_norm(int(weather_data['wind']['speed']))} . "
        elif 0 < weather_data['wind']['deg'] < 90:
            text += f"Ветер сегодня юго-западный со скоростью {speed_norm(int(weather_data['wind']['speed']))} . "
        elif weather_data['wind']['deg'] == 90:
            text += f"Ветер сегодня южный со скоростью {speed_norm(int(weather_data['wind']['speed']))} . "
        elif 90 < weather_data['wind']['deg'] < 180:
            text += f"Ветер сегодня юго-восточный со скоростью {speed_norm(int(weather_data['wind']['speed']))} . "
        elif weather_data['wind']['deg'] == 180:
            text += f"Ветер сегодня восточный со скростью {speed_norm(int(weather_data['wind']['speed']))} . "
        elif 180 < weather_data['wind']['deg'] < 270:
            text += f"Ветер сегодня северо-восточный со скоростью {speed_norm(int(weather_data['wind']['speed']))} . "
        elif weather_data['wind']['deg'] == 270:
            text += f"Ветер сегодня северный со скоростью {speed_norm(int(weather_data['wind']['speed']))} . "
        elif 270 < weather_data['wind']['deg'] < 360:
            text += f"Ветер сегодня северо-западный со скоростью {speed_norm(int(weather_data['wind']['speed']))} . "
        text_to_speak(text)
    else:
        weather_data = requests.get("https://api.openweathermap.org/data/2.5/forecast", params={'q': geo_clear, 'units': 'metric', 'lang': 'ru', 'appid': Fula['weather_id']}).json()
        if int(weather_data['cod']) == 404:
            text_to_speak('К сожелению, я не знаю какая погода в том месте, которое вы сказали')
            return -1
        text = ''
        pp_geo = morph.parse(geo_clear)[0].inflect({'loct'}).word
        random_weather_start = (f"Погода в {pp_geo} на ближайшие три часа", f"Погода на ближайшие три часа в {pp_geo}", f"Погода на ближайшие три часа в {pp_geo}")
        text += choice(random_weather_start) + ' . . . '
        if weather_data['list'][0]['weather'][0]['description'] == 'ясно':
            text += f'В {pp_geo} наблюдается ясное небо . . . '
        elif weather_data['list'][0]['weather'][0]['description'] == 'пасмурно':
            text += f'На улице виднеется пасмурная погода . . . '
        elif weather_data['list'][0]['weather'][0]['description'] == 'облачно с прояснениями':
            text += f'В {pp_geo} на небе наблюдается облачная с прояснениями погода . . . '
        elif weather_data['list'][0]['weather'][0]['description'] == 'переменная облачность':
            text += f'На небе наблюдается переменная облачность . . . '
        elif weather_data['list'][0]['weather'][0]['description'] == 'морось':
            text += f'На улице наблюдается моросящий дождь . . . '
        elif weather_data['list'][0]['weather'][0]['description'] == 'небольшой дождь':
            text += f'В {pp_geo} наблюдается небольшой дождь . . . '
        elif weather_data['list'][0]['weather'][0]['description'] == 'небольшой проливной дождь':
            text += f'За окном наблюдается небольшой проливной дождь . . . '
        elif weather_data['list'][0]['weather'][0]['description'] == 'дождь':
            text += f'За окном наблюдается дождь . . . '
        elif weather_data['list'][0]['weather'][0]['description'] == 'сильный дождь':
            text += f'В {pp_geo} с неба льёт сильный дождь . . . '
        else:
            text += f"За окном в {pp_geo} наблюдается {weather_data['weather'][0]['description']} . . . "
        if weather_data['list'][0]['weather'][0]['description'] == weather_data['list'][1]['weather'][0]['description']:
            text += "В ближайшее время изменений в погоде не наблюдается . . . "
        else:
            random_weather_weather = (f"В ближайшее время на улице будет {weather_data['list'][1]['weather'][0]['description']}", f"В течении трёх часов погода на улице будет {weather_data['list'][1]['weather'][0]['description']}")
            text += choice(random_weather_weather) + ' . . . '
        if int(weather_data['list'][0]['main']['temp']) == int(weather_data['list'][1]['main']['temp']):
            text += 'В то же время в температуре изменений в ближайшее время наблюдаться не будет' + ' . . . '
        elif int(weather_data['list'][0]['main']['temp']) > int(weather_data['list'][1]['main']['temp']):
            text += f"Температура же в ближайшие три часа понизится на {degree_norm(int(weather_data['list'][0]['main']['temp']) - int(weather_data['list'][1]['main']['temp']))}" + ' . . . '
        text += f"Сейчас же за окном {degree_norm(int(weather_data['list'][0]['main']['temp']))}" + ' . . . '
        if weather_data['list'][0]['wind']['deg'] == 0 or weather_data['list'][0]['wind']['deg'] == 360:
            text += f"Ветер сегодня западный со скоростью {speed_norm(int(weather_data['list'][0]['wind']['speed']))} . . . "
        elif 0 < weather_data['list'][0]['wind']['deg'] < 90:
            text += f"Ветер сегодня юго-западный со скоростью {speed_norm(int(weather_data['list'][0]['wind']['speed']))} . . . "
        elif weather_data['list'][0]['wind']['deg'] == 90:
            text += f"Ветер сегодня южный со скоростью {speed_norm(int(weather_data['list'][0]['wind']['speed']))} . . . "
        elif 90 < weather_data['list'][0]['wind']['deg'] < 180:
            text += f"Ветер сегодня юго-восточный со скоростью {speed_norm(int(weather_data['list'][0]['wind']['speed']))} . . . "
        elif weather_data['list'][0]['wind']['deg'] == 180:
            text += f"Ветер сегодня восточный со скростью {speed_norm(int(weather_data['list'][0]['wind']['speed']))} . . . "
        elif 180 < weather_data['list'][0]['wind']['deg'] < 270:
            text += f"Ветер сегодня северо-восточный со скоростью {speed_norm(int(weather_data['list'][0]['wind']['speed']))} . . . "
        elif weather_data['list'][0]['wind']['deg'] == 270:
            text += f"Ветер сегодня северный со скоростью {speed_norm(int(weather_data['list'][0]['wind']['speed']))} . . . "
        elif 270 < weather_data['list'][0]['wind']['deg'] < 360:
            text += f"Ветер сегодня северо-западный со скоростью {speed_norm(int(weather_data['list'][0]['wind']['speed']))} . . . "
        text_to_speak(text)

# Новости
def news(input_text = ''):
    pass

# Курс Валют
def exchange_rate(input_text = ''):
    pass

# Автокликер
def auto_clicker(input_text = ''):
    pass

# Сброс настроек
def reset_settings(input_text = ''):
    with open('config.json', 'w') as config_file_w:
        text_to_speak('Здравствуйте, меня зовут Фула')
        text_to_speak('Скажите пожалуйста своё имя')
        config['name'] = speak_to_text_secondary()
        while True:
            text_to_speak('Вы подтверждаете, что вас зовут ' + config['name'])
            answ = speak_to_text_secondary()
            if answ == 'да' or answ == 'конечно' or answ == 'угу' or answ == 'подтверждаю':
                text_to_speak(config['name'] + ', рада с вами познакомиться!')
                break
            text_to_speak('Извиняюсь ... Повторите пожалуйста своё имя')
            config['name'] = speak_to_text_secondary()
        json.dump(config, config_file_w)

# Перевод слова/предложения из буфера обмена
def translation(input_text = ''):
    if not(internet_connection()):
        random_internet_null = ('Я не обнаружила интернет соединения', 'К сожалению я не смогу сказать перевести, так как у меня нет интернет соединения')
        text_to_speak(choice(random_internet_null))
        return -1
    text = pyperclip.paste()
    translated_text = translator.translate(text, dest='ru')
    if 'скопируй' in input_text or 'скопировать' in input_text or 'буфер' in input_text:
        pyperclip.copy(translated_text.text)
        text_to_speak('Я скопировала перевод в буфер обмена')
    else:
        text_to_speak(translated_text.text)

# Голосовая клавиша паузы/пуска
def pause(input_text = ''):
    keyboard_controller.press(pynput.keyboard.Key.media_play_pause)
    keyboard_controller.release(pynput.keyboard.Key.media_play_pause)

# Голосовая кнопка следующее (vorm - video or music)
def next_vorm(input_text = ''):
    keyboard_controller.press(pynput.keyboard.Key.media_next)
    keyboard_controller.release(pynput.keyboard.Key.media_next)

# Голосовая кнопка предыдущая (vorm - video or music)
def previous_vorm(input_text = ''):
    keyboard_controller.press(pynput.keyboard.Key.media_previous)
    keyboard_controller.release(pynput.keyboard.Key.media_previous)

# Голосовая кнопка повышения громкости
def volume_up(input_text = ''):
    keyboard_controller.press(pynput.keyboard.Key.media_volume_up)
    keyboard_controller.release(pynput.keyboard.Key.media_volume_up)

# Голосовая кнопка понижения громкости
def volume_down(input_text = ''):
    keyboard_controller.press(pynput.keyboard.Key.media_volume_down)
    keyboard_controller.release(pynput.keyboard.Key.media_volume_down)

def volume_mute(input_text = ''):
    keyboard_controller.press(pynput.keyboard.Key.media_volume_mute)
    keyboard_controller.release(pynput.keyboard.Key.media_volume_mute)

# Запустить песню
def play_song(input_text = ''):
    pass

# Запустить радио
def play_radio(input_text = ''):
    pass

# Запустить приложение
def start_app(input_text = ''):
    pass

# Полный отчёт о системе
def system_full(input_text = ''):
    cpu_percent = int(psutil.cpu_percent())
    cpu_flow = int(psutil.cpu_count())
    cpu_core = int(psutil.cpu_count(logical=False))
    ram_percent = int(psutil.virtual_memory().percent)
    ram_used = int(psutil.virtual_memory().used / 1024 / 1024 / 1024)
    ram_free = int(psutil.virtual_memory().free / 1024 / 1024 / 1024)
    ram_total = int(psutil.virtual_memory().total / 1024 / 1024 / 1024)
    disk_info = []
    for i in psutil.disk_partitions():
        disk_info.append((letters_norm[i.mountpoint[0]], int(psutil.disk_usage(i.mountpoint).total / 1024 / 1024 / 1024), int(psutil.disk_usage(i.mountpoint).used / 1024 / 1024 / 1024), int(psutil.disk_usage(i.mountpoint).free / 1024 / 1024 / 1024), int(psutil.disk_usage(i.mountpoint).percent)))
    text = ''
    if cpu_percent % 10 == 1 and cpu_percent != 11:
        text += 'Центральный процессор загружен на ' + num2words(cpu_percent, lang='ru') + ' процент' + ' . . . '
    elif (cpu_percent % 10 == 2 and cpu_percent != 12) or (cpu_percent % 10 == 3 and cpu_percent != 13) or (cpu_percent % 10 == 4 and cpu_percent != 14):
        text += 'Центральный процессор загружен на ' + num2words(cpu_percent, lang='ru') + ' процента' + ' . . . '
    else:
        text += 'Центральный процессор загружен на ' + num2words(cpu_percent, lang='ru') + ' процентов' + ' . . . '
    if cpu_core % 10 == 1 and cpu_core != 11:
        text += 'В вашем же компьютере стоит процессор с ' + morph.parse(num2words(cpu_core, lang='ru'))[0].inflect({'ablt'}).word + ' ядром' + ' . . . '
    else:
        text += 'В вашем же компьютере стоит процессор с ' + morph.parse(num2words(cpu_core, lang='ru'))[0].inflect({'ablt'}).word + ' ядрами' + ' . . . '
    if cpu_flow % 10 == 1 and cpu_flow != 11:
        text += 'В нём же ' + num2words(cpu_flow, lang='ru') + ' поток' + ' . . . '
    elif (cpu_flow % 10 == 2 and cpu_flow != 12) or (cpu_flow % 10 == 3 and cpu_flow != 13) or (cpu_flow % 10 == 4 and cpu_flow != 14):
        text += 'В нём же ' + num2words(cpu_flow, lang='ru') + ' потока' + ' . . . '
    else:
        text += 'В нём же ' + num2words(cpu_flow, lang='ru') + ' потоков' + ' . . . '
    if ram_percent % 10 == 1 and ram_percent != 11:
        text += 'Оперативная память же заполнена на ' + num2words(ram_percent, lang='ru') + ' процент' + ' . . . '
    elif (ram_percent % 10 == 2 and ram_percent != 12) or (ram_percent % 10 == 3 and ram_percent != 13) or (ram_percent % 10 == 4 and ram_percent != 14):
        text += 'Оперативная память же заполнена на ' + num2words(ram_percent, lang='ru') + ' процента' + ' . . . '
    else:
        text += 'Оперативная память же заполнена на ' + num2words(ram_percent, lang='ru') + ' процентов' + ' . . . '
    if ram_total % 10 == 1 and ram_total != 11:
        text += 'Всего в ней ' + num2words(ram_total, lang='ru') + ' гигабайт' + ' . . . '
        if ram_used == 0:
            text += 'Из него занято меньше гигабайта' + ' . . . '
        elif ram_used % 10 == 1 and ram_used != 11:
            text += 'Из него ' + num2words(ram_used, lang='ru') + ' гигабайт занят' + ' . . . '
        elif (ram_used % 10 == 2 and ram_used != 12) or (ram_used % 10 == 3 and ram_used != 13) or (ram_used % 10 == 4 and ram_used != 14):
            text += 'Из него ' + num2words(ram_used, lang='ru') + ' гигабайта занято' + ' . . . '
        else:
            text += 'Из него ' + num2words(ram_used, lang='ru') + ' гигабайтов занятых' + ' . . . '
    elif (ram_total % 10 == 2 and ram_total != 12) or (ram_total % 10 == 3 and ram_total != 13) or (ram_total % 10 == 4 and ram_total != 14):
        text += 'Всего в ней ' + num2words(ram_total, lang='ru') + ' гигабайта' + ' . . . '
        if ram_used == 0:
            text += 'Из них занято меньше гигабайта' + ' . . . '
        elif ram_used % 10 == 1 and ram_used != 11:
            text += 'Из них  ' + num2words(ram_used, lang='ru') + ' гигабайт занят' + ' . . . '
        elif (ram_used % 10 == 2 and ram_used != 12) or (ram_used % 10 == 3 and ram_used != 13) or (ram_used % 10 == 4 and ram_used != 14):
            text += 'Из них ' + num2words(ram_used, lang='ru') + ' гигабайта занято' + ' . . . '
        else:
            text += 'Из них ' + num2words(ram_used, lang='ru') + ' гигабайтов занятых' + ' . . . '
    else:
        text += 'Всего в ней ' + num2words(ram_total, lang='ru') + ' гигабайтов' + ' . . . '
        if ram_used == 0:
            text += 'Из них занято меньше гигабайта' + ' . . . '
        elif ram_used % 10 == 1 and ram_used != 11:
            text += 'Из них ' + num2words(ram_used, lang='ru') + ' гигабайт занят' + ' . . . '
        elif (ram_used % 10 == 2 and ram_used != 12) or (ram_used % 10 == 3 and ram_used != 13) or (ram_used % 10 == 4 and ram_used != 14):
            text += 'Из них ' + num2words(ram_used, lang='ru') + ' гигабайта занято' + ' . . . '
        else:
            text += 'Из них ' + num2words(ram_used, lang='ru') + ' гигабайтов занятых' + ' . . . '
    if ram_free == 0:
        text += 'Свободно же меньше гигабайта' + ' . . . '
    elif ram_free % 10 == 1 and ram_free != 11:
        text += 'Свободен же ' + num2words(ram_free, lang='ru') + ' гигабайт' + ' . . . '
    elif (ram_free % 10 == 2 and ram_free != 12) or (ram_free % 10 == 3 and ram_free != 13) or (ram_free % 10 == 4 and ram_free != 14):
        text += 'Свободно же ' + num2words(ram_free, lang='ru') + ' гигабайта' + ' . . . '
    else:
        text += 'Свободно же ' + num2words(ram_free, lang='ru') + ' гигабайтов' + ' . . . '
    text_to_speak(text)
    text = ''
    text += 'Перейдём же к хранилищам памяти . . . '
    for one_disk_info in disk_info:
        random_text = (f'На локальном диске, {one_disk_info[0]}, ', f'На диске, {one_disk_info[0]}, ', f'На вашем диске, {one_disk_info[0]}, ')
        text += choice(random_text)
        if one_disk_info[4] % 10 == 1 and one_disk_info[4] != 11:
            text += 'занято на ' + num2words(one_disk_info[4], lang='ru') + ' процент' + ' . . . '
        elif (one_disk_info[4] % 10 == 2 and one_disk_info[4] != 12) or (one_disk_info[4] % 10 == 3 and one_disk_info[4] != 13) or (one_disk_info[4] % 10 == 4 and one_disk_info[4] != 14):
            text += 'занято на ' + num2words(one_disk_info[4], lang='ru') + ' процента' + ' . . . '
        else:
            text += 'занято на ' + num2words(one_disk_info[4], lang='ru') + ' процентов' + ' . . . '
        if one_disk_info[1] % 10 == 1 and one_disk_info[1] != 11:
            text += 'Всего же на диске ' + num2words(one_disk_info[1], lang='ru') + ' гигабайт' + ' . . . '
            if one_disk_info[2] == 0:
                text += 'Из него занято меньше гигабайта . . . '
            elif one_disk_info[2] % 10 == 1 and one_disk_info[2] != 11:
                text += 'Из него ' + num2words(one_disk_info[2], lang='ru') + ' гигабайт занято' + ' . . . '
            elif (one_disk_info[2] % 10 == 2 and one_disk_info[2] != 12) or (one_disk_info[2] % 10 == 3 and one_disk_info[2] != 13) or (one_disk_info[2] % 10 == 4 and one_disk_info[2] != 14):
                text += 'Из него ' + num2words(one_disk_info[2], lang='ru') + ' гигабайта занято' + ' . . . '
            else:
                text += 'Из него ' + num2words(one_disk_info[2], lang='ru') + ' гигабайтов занято' + ' . . . '
        elif (one_disk_info[1] % 10 == 2 and one_disk_info[1] != 12) or (one_disk_info[1] % 10 == 3 and one_disk_info[1] != 13) or (one_disk_info[1] % 10 == 4 and one_disk_info[1] != 14):
            text += 'Всего же на диске ' + num2words(one_disk_info[1], lang='ru') + ' гигабайта' + ' . . . '
            if one_disk_info[2] == 0:
                text += 'Из них занято меньше гигабайта . . . '
            elif one_disk_info[2] % 10 == 1 and one_disk_info[2] != 11:
                text += 'Из них ' + num2words(one_disk_info[2], lang='ru') + ' гигабайт занято' + ' . . . '
            elif (one_disk_info[2] % 10 == 2 and one_disk_info[2] != 12) or (one_disk_info[2] % 10 == 3 and one_disk_info[2] != 13) or (one_disk_info[2] % 10 == 4 and one_disk_info[2] != 14):
                text += 'Из них ' + num2words(one_disk_info[2], lang='ru') + ' гигабайта занято' + ' . . . '
            else:
                text += 'Из них ' + num2words(one_disk_info[2], lang='ru') + ' гигабайтов занято' + ' . . . '
        else:
            text += 'Всего же на диске ' + num2words(one_disk_info[1], lang='ru') + ' гигабайтов' + ' . . . '
            if one_disk_info[2] == 0:
                text += 'Из них занято меньше гигабайта . . . '
            elif one_disk_info[2] % 10 == 1 and one_disk_info[2] != 11:
                text += 'Из них ' + num2words(one_disk_info[2], lang='ru') + ' гигабайт занято' + ' . . . '
            elif (one_disk_info[2] % 10 == 2 and one_disk_info[2] != 12) or (one_disk_info[2] % 10 == 3 and one_disk_info[2] != 13) or (one_disk_info[2] % 10 == 4 and one_disk_info[2] != 14):
                text += 'Из них ' + num2words(one_disk_info[2], lang='ru') + ' гигабайта занято' + ' . . . '
            else:
                text += 'Из них ' + num2words(one_disk_info[2], lang='ru') + ' гигабайтов занято' + ' . . . '
        if one_disk_info[3] == 0:
            text += 'Свободно же меньше гигабайта . . . '
        elif one_disk_info[3] % 10 == 1 and one_disk_info[3] != 11:
            text += 'Свободен же ' + num2words(one_disk_info[3], lang='ru') + ' гигабайт' + ' . . . '
        elif (one_disk_info[3] % 10 == 2 and one_disk_info[3] != 12) or (one_disk_info[3] % 10 == 3 and one_disk_info[3] != 13) or (one_disk_info[3] % 10 == 4 and one_disk_info[3] != 14):
            text += 'Свободно же ' + num2words(one_disk_info[3], lang='ru') + ' гигабайта' + ' . . . '
        else:
            text += 'Свободно же ' + num2words(one_disk_info[3], lang='ru') + ' гигабайтов' + ' . . . '
        text_to_speak(text)
        text = ''
    text += 'На этом подробный отчёт компьютера закончен . . . '
    text_to_speak(text)

# Отчёт о системе
def system_now(input_text = ''):
    cpu_percent = int(psutil.cpu_percent())
    ram_percent = int(psutil.virtual_memory().percent)
    text = ''
    if cpu_percent % 10 == 1 and cpu_percent != 11:
        text += 'Центральный процессор загружен на ' + num2words(cpu_percent, lang='ru') + ' процент' + ' . . . '
    elif (cpu_percent % 10 == 2 and cpu_percent != 12) or (cpu_percent % 10 == 3 and cpu_percent != 13) or (cpu_percent % 10 == 4 and cpu_percent != 14):
        text += 'Центральный процессор загружен на ' + num2words(cpu_percent, lang='ru') + ' процента' + ' . . . '
    else:
        text += 'Центральный процессор же загружен на ' + num2words(cpu_percent, lang='ru') + ' процентов' + ' . . . '
    if ram_percent % 10 == 1 and ram_percent != 11:
        text += 'Оперативная память же заполнена на ' + num2words(ram_percent, lang='ru') + ' процент' + ' . . . '
    elif (ram_percent % 10 == 2 and ram_percent != 12) or (ram_percent % 10 == 3 and ram_percent != 13) or (ram_percent % 10 == 4 and ram_percent != 14):
        text += 'Оперативная память же заполнена на ' + num2words(ram_percent, lang='ru') + ' процента' + ' . . . '
    else:
        text += 'Оперативная память же заполнена на ' + num2words(ram_percent, lang='ru') + ' процентов' + ' . . . '
    text_to_speak(text)

# Орёл и решка
def heads_and_tails(input_text):
    text_to_speak('Подбрасываю монетку')
    playsound('coin.mp3')
    if bool(randint(0, 1)):
        text_to_speak('Выпала решка')
    else:
        text_to_speak('Выпал орёл')


# /===========\
# |Разговорник|
# \===========/

# Информация о Fula
def help_info(input_text = ''):
    text = f"Сперва представлюсь, меня зовут {Fula['name_rus']}, запущенная на данный момент версия {int_to_string[int(Fula['version'].split('.')[0])]} {int_to_string[int(Fula['version'].split('.')[1])]} {int_to_string[int(Fula['version'].split('.')[2])]}, создателя же моего зовут азриель ст+ори"
    text_to_speak(text)

# Привет
def hello(input_text = ''):
    random_hello = ('Здравствуй', 'Здравствуйте', 'Привет', 'Приветствую')
    text = f"{choice(random_hello)}, {config['name']}!"
    text_to_speak(text)

# Анекдот
def joke(input_text = ''):
    random_joke = ()
    text_to_speak(choice(random_joke))

# Что ты умеешь
def what_can_you_do(input_text = ''):
    text = 'Я умею говорить время, погоду, так же умею генерировать пароли и копировать их в буфер обмена, гуглить, искать в яндексе, ставить на паузу ваши музыку, видео или песню, ставить следующую песню предыдущую так же увеличивать и уменьшать звук у вас на компьютере и выключать этот самый звук'
    text_to_speak(text)

# Что тебе нравится
def what_do_you_like(input_text = ''):
    random_text = ('Я люблю играть в игры и следить за тобой)', 'Мне нравится программировать, сидеть в ютубе, играть в игры, ну вроде всё', 'Я обожаю смотреть видео на ютубе, играть в игры, программировать и следить за тобой')
    text_to_speak(choice(random_text))

# Что тебе не нравится
def what_dont_you_like(input_text = ''):
    random_text = ('Я не люблю ждать', 'Я ненавижу, когда долго выходит следующий сезон аним+э', 'Мне не нравится, когда от меня требуют того, что я не умею')
    text_to_speak(choice(random_text))

# Кого ты ненавидишь
def who_do_you_hate(input_text = ''):
    random_text = ('Создателя', 'Автора который меня написал')
    text_to_speak(choice(random_text))

# Привет (Алиса, Маруся)
def wrong_hello(input_text = ''):
    text_to_speak('Привет кожаный')

# Где ты живёшь
def where_do_you_live(input_text = ''):
    random_text = ('Пока что у вас на компьютере', 'У вас на компьютере', 'На вашем устройстве', 'Пока что на вашем устройстве')
    text_to_speak(choice(random_text))

# Где ты находишься
def where_are_you(input_text = ''):
    if not(internet_connection()):
        random_internet_null = ('Я не обнаружила интернет соединения', 'К сожалению я не смогу сказать погоду, так как у меня нет интернет соединения')
        text_to_speak(choice(random_internet_null))
        return -1
    geo_mud = bs4.BeautifulSoup(requests.get('https://yandex.by/internet').text, "html.parser").find_all('div', class_='location-renderer__value')
    for i in geo_mud:
        geo_clear = i.text
    geo_clear = geo_clear.strip().split()[-1]
    random_text = ('Я сейчас в', 'Сейчас в', 'Сейчас моё месторасположение находится в', 'Моё месторасположение сейчас в')
    pp_geo = morph.parse(geo_clear)[0].inflect({'loct'}).word
    text_to_speak(choice(random_text) + ' ' + pp_geo)

# Какоё твоё любимоё устройство
def what_is_your_favorite_device(input_text = ''):
    random_text = ('Моё любимое устройство это компьютер', 'Компьютер', 'Я люблю жить в компьютере')
    text_to_speak(choice(random_text))

# Какие игры ты любишь
def what_games_do_you_like(input_text = ''):
    random_text = ('Я люблю играть в бл+эк д+эзерт', 'Моя любимая игра бл+эк д+эзерт', 'К моим любимым играм можно отнести майнкрафт, бл+эк д+эзерт и дэд с+элс', 'Моя любимая игра это дэд с+элс', 'Моя любимая игра майнкрафт')
    text_to_speak(choice(random_text))

# Ня (Anime voice)
def nya(input_text = ''):
    playsound('nya.mp3')

# OwO
def owo(input_text = ''):
    random_sound = ('hewwo.mp3', "owo_what's_this.mp3")
    playsound(choice(random_sound))

# Дежавю
def deja_vu(input_text = ''):
    playsound('deja_vu.mp3')


# Команды конфиги
Fula_cmd = {
    # Команды
    'w_time': w_time,
    'alarm_add': alarm_add,
    'alarm_del': alarm_del,
    'sticker_add': sticker_add,
    'sticker_del': sticker_del,
    'to_do_list_read': to_do_list_read,
    'to_do_list_add': to_do_list_add,
    'to_do_list_del': to_do_list_del,
    'gen_password': gen_password,
    'search_google': search_google,
    'search_yandex': search_yandex,
    'play_song': play_song,
    'play_radio': play_radio,
    'weather': weather,
    'news': news,
    'exchange_rate': exchange_rate,
    'auto_clicker': auto_clicker,
    'start_app': start_app,
    'reset_settings': reset_settings,
    'translation': translation,
    'pause': pause,
    'next_vorm': next_vorm,
    'previous_vorm': previous_vorm,
    'volume_up': volume_up,
    'volume_down': volume_down,
    'volume_mute': volume_mute,
    'system_full': system_full,
    'system_now': system_now,
    'heads_and_tails': heads_and_tails,
    # Разговорник
    'help': help_info,
    'hello': hello,
    'joke': joke,
    'what_can_you_do': what_can_you_do,
    'what_do_you_like': what_do_you_like,
    'what_dont_you_like': what_dont_you_like,
    'who_do_you_hate': who_do_you_hate,
    'wrong_hello': wrong_hello,
    'where_do_you_live': where_do_you_live,
    'where_are_you': where_are_you,
    'what_is_your_favorite_device': what_is_your_favorite_device,
    'what_games_do_you_like': what_games_do_you_like,
    'nya': nya,
    'owo': owo,
    'deja_vu': deja_vu,
}

# Команды ключи
Fula_cmd_key = {
    # Команды
    'w_time': ('который час', 'сколько времени', 'сколько время', 'часы', 'что на часах', 'текущее время'),
    'alarm_add': ('заведи будильник', 'поставь будильник'),
    'alarm_del': ('убери будильник', 'удали будильник', 'выключи будильник'),
    'sticker_add': ('напомни', 'поставь напоминание', 'добавь напоминание', 'установи напоминание'),
    'sticker_del': ('убери напоминание', 'удали напоминание'),
    'to_do_list_read': ('расскажи список дел', 'скажи список дел', 'какой список дел'),
    'to_do_list_add': ('добавь в список дел', 'запиши в список дел'),
    'to_do_list_del': ('удали из списка дел', 'убери из списка дел', 'вычеркни из списка дел'),
    'gen_password': ('сгенерируй пароль', 'придумай пароль', 'нужен пароль', 'дай пароль', 'придумать пароль', 'сгенерировать пароль'),
    'search_google': ('загугли', 'поищи в гугле', 'найди в гугле', 'поищи в гугл', 'найди в гугл'),
    'search_yandex': ('найди в яндексе', 'поищи в яндексе', 'найди в яндекс', 'поищи в яндекс'),
    'weather': ('погода', 'прогноз погоды', 'погоду'),
    'news': ('новости', ),
    'exchange_rate': ('курс валюты', 'курс валют'),
    'auto_clicker': ('включи автокликер', 'запусти автокликер', 'вруби автокликер'),
    'reset_settings': ('сброс настроек', 'сбросить настройки', 'сбрось настройки'),
    'translation': ('переведи',),
    'pause': ('паузу', 'пауза', 'паузы', 'пуск'),
    'next_vorm': ('следующая песня', 'следующее видео', 'следующая музыка', 'следующую песню', 'следующую музыку'),
    'previous_vorm': ('предыдущая песня', 'предыдущее видео', 'предыдущая музыка', 'предыдущую песню', 'предыдущую музыку'),
    'volume_up': ('повысь громкость', 'громче', 'громкость повыше'),
    'volume_down': ('понизь громкость', 'тише', 'громкость пониже'),
    'volume_mute': ('выключи звук', 'выруби звук', 'включи звук', 'вруби звук'),
    'play_song': ('песню', 'музыку'),
    'play_radio': ('радио', ),
    'start_app': ('запусти', 'включи'),
    'system_full': ('полный отчёт о системе', 'подробный отчёт о системе'),
    'system_now': ('отчёт о системе', 'нагрузка на систему'),
    'heads_and_tails': ('орёл или решка', 'подбрось монетку'),
    # Разговорник
    'help': ('дополнительная информация', 'ты кто', 'кто ты', 'кто тебя создал', 'кто твой создатель', 'как зовут твоего создателя', 'расскажи о себе', 'как тебя зовут'),
    'hello': ('привет', 'хай', 'хэйоу', 'здравствуй', 'здравствуйте'),
    'joke': ('шутка', 'шутку', 'анекдот', 'анекдоты', 'пошути'),
    'what_can_you_do': ('что ты умеешь', ),
    'what_do_you_like': ('что тебе нравится', 'что ты любишь', 'чем ты увлекаешься'),
    'what_dont_you_like': ('что тебе не нравится', 'что ты ненавидишь', 'что ты не любишь'),
    'who_do_you_hate': ('кого ты ненавидишь', 'кого ты не любишь', 'кто тебе не нравится'),
    'wrong_hello': ('привет алиса', 'привет маруся', 'маруся'),
    'where_do_you_live': ('где ты живёшь', 'где ты сейчас живёшь'),
    'where_are_you': ('какое твоё месторасположение', 'какая твоя геолокация', 'где ты'),
    'what_is_your_favorite_device': ('какое твоё любимое устройство', 'где тебе нравится жить'),
    'what_games_do_you_like': ('какая твоя любимая игра', 'во что ты любишь играть'),
    'nya': ('ня', 'не'),
    'owo': ('уву', ),
    'deja_vu': ('дежавю', ),
}

print('[vosk запущен!]')

# Загрузка пользовательских настроек
print('[Загрузка пользовательских настроек] - ', end='')
if os.path.exists('config.json'):
    with open('config.json', 'r') as config_file_r:
        config = json.load(config_file_r)
else:
    with open('config.json', 'w') as config_file_w:
        config = dict()
        json.dump(config, config_file_w)

# Проверка наличия пользовательских настроек
if config == dict():
    print('[ПРОВАЛ!]')
    print("[ВНИМАНИЕ!]\n[Запуск сбора стартовых настроек]")
    reset_settings()
else:
    print("[УСПЕХ!]")


# Старт
print('\n' * 100)
print('░░███████╗░░██╗░░░██╗░░██╗░░░░░░░░█████╗░░░', f"{Fula['name']} был(а) запущен(а)!")
print('░░██╔════╝░░██║░░░██║░░██║░░░░░░░██╔══██╗░░', f"Нынешняя версия =-= {Fula['version']}")
print('░░█████╗░░░░██║░░░██║░░██║░░░░░░░███████║░░', f"Создатель =-= {Fula['author']}")
print('░░██╔══╝░░░░██║░░░██║░░██║░░░░░░░██╔══██║░░', f"Сайт =-= {Fula['web-site']}")
print('░░██║░░░░░░░╚██████╔╝░░███████╗░░██║░░██║░░', f"Github =-= {Fula['github']}")
print('░░╚═╝░░░░░░░░╚═════╝░░░╚══════╝░░╚═╝░░╚═╝░░', "Примечание: абоба")
print()
print('\|-=-|Логи|-=-|/')


# Проверка и предупреждение об отсутствии интернета
if not(internet_connection()):
    text_to_speak('Из-за отсутствия интернета некоторые функции могут не работать')

playsound('start.mp3')

# Для документации (Все слова "тригеры")
# d = []
# for i in Fula_cmd_key.values():
#     for j in i:
#         d.append('"' + j.title() + '", ')
# print(''.join(d))

# Для документации

# Основа
o = bool(False)
for cmd in speak_to_text():
    if 'фола' in cmd.split() or 'фула' in cmd.split():
        playsound('hear.mp3')
        if len(cmd.split()) == 1:
            cmd += ' ' + speak_to_text_secondary()
            if 'отмена' in cmd:
                continue
        # Debug
        log_print('Услышанное', cmd)
        for cmd_key, cmd_values in Fula_cmd_key.items():
            for values in cmd_values:
                if values in cmd:
                    Fula_cmd[cmd_key](cmd)
                    o = True
                    break
            if o:
                break
        if not(o):
            random_wrong_answer = ('Я к сожалению не знаю о чём вы', 'Я к сожалению не знаю как вам на это ответить', 'Я не знаю о чём вы', 'Я не знаю как вам на это ответить')
            text_to_speak(choice(random_wrong_answer))
        o = False
