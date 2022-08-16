# Добавить синтезатор речи на двух языках

# Переобдуманный первый голосовой помощник (Ozeta)
from vosk import Model, KaldiRecognizer  # STT
from random import choice
import torch  # Silero (TTS)
import sounddevice
import webbrowser
import pymorphy2
import pyperclip
import requests
import pyaudio
import string
import socket
import pynput
import numpy
import time
import json
import bs4
import os

#k = pynput.keyboard.Controller()
#k.press(pynput.keyboard.Key.media_play_pause)
#k.release(pynput.keyboard.Key.media_play_pause)

# Конфиги Fula
Fula = {
    'name': 'Fula',
    'name_rus': 'фула',
    'version': '0.0.2',
    'author': 'Asriel_Story',
    'web-site': '...',
    'github': 'https://github.com/AsrielStory/Fula_AI',
    'weather_id': 'f76f1c4ed170f79ddea0b7862b53ecae',
}


# Вывод в формате логов
def log_print(key, text):
    print('[' + time.ctime() + ']', "[" + key + "]", text)

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


# Команды

# Информация о Fula
def help_info(input_text = ''):
    text = f"Сперва представлюсь, меня зовут {Fula['name_rus']}, запущенная на данный момент версия {int_to_string[int(Fula['version'].split('.')[0])]} {int_to_string[int(Fula['version'].split('.')[1])]} {int_to_string[int(Fula['version'].split('.')[2])]}, создателя же моего зовут азриель ст+ори"
    text_to_speak(text)

# Привет
def hello(input_text = ''):
    random_hello = ('Здравствуй', 'Здравствуйте', 'Привет', 'Приветствую')
    text = f"{choice(random_hello)}, {config['name']}!"
    text_to_speak(text)

# Время
def w_time(input_text = ''):
    hour = time.strftime("%H")
    minute = time.strftime("%M")
    text = f"{int_to_string[hour]} {hours_norm[hour]} {minute_norm(minute)}"
    text_to_speak(text)

# Анекдот
def joke(input_text = ''):
    random_joke = ()
    text_to_speak(choice(random_joke))

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

# Запустить песню
def play_song(input_text = ''):
    pass

# Запустить радио
def play_radio(input_text = ''):
    pass

# Погода
def weather(input_text = ''):
    if not(internet_connection()):
        random_internet_null = ('Я не обнаружила интернет соединения', 'К сожалению я не смогу сказать погоду, так как у меня нет интернет соединения', 'Я не смогу рассказать про погоду, так как нету интернет соединения')
        text_to_speak(choice(random_internet_null))
        return 0
    if ('в' in input_text or 'на' in input_text or 'во' in input_text) and not('сегодня' in input_text or 'понедельник' in input_text or 'вторник' in input_text or 'среду' in input_text or 'четверг' in input_text or 'пятницу' in input_text or 'суботу' in input_text or 'воскресенье' in input_text) and not(input_text.split().count('во') + input_text.split().count('в') + input_text.split().count('на') == 1 and 'завтра' in input_text):
        if 'в' in input_text.split():
            index_key = 'в'
        elif 'во' in input_text.split():
            index_key = 'во'
        elif 'на' in input_text.split():
            index_key = 'на'
        geo_clear = input_text.split()[input_text.split().index(index_key) + 1]
        try:
            geo_clear = morph.parse(geo_clear)[0].inflect({'nomn'}).word
        except AttributeError:
            text_to_speak('К сожелению, я не знаю какая погода в том месте, которое вы сказали')
            return -1
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

# OwO?
def repeat(input_text = ''):
    text_to_speak(input_text)

# Запустить приложение
def start_app(input_text = ''):
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
def translation():
    pass


# Команды конфиги
Fula_cmd = {
    'help': help_info,
    'hello': hello,
    'w_time': w_time,
    'joke': joke,
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
    'repeat': repeat,
    'start_app': start_app,
    'reset_settings': reset_settings,
    'translation': translation,
}

# Команды ключи
Fula_cmd_key = {
    'help': ('дополнительная информация', 'ты кто', 'кто ты', 'кто тебя создал', 'кто твой создатель', 'как зовут твоего создателя', 'расскажи о себе', 'как тебя зовут'),
    'hello': ('привет', 'хай', 'хэйоу', 'здравствуй', 'здравствуйте'),
    'w_time': ('который час', 'сколько времени', 'сколько время', 'часы', 'что на часах', 'текущее время'),
    'joke': ('шутка', 'шутку', 'анекдот', 'анекдоты', 'пошути'),
    'alarm_add': ('заведи будильник', 'поставь будильник'),
    'alarm_del': ('убери будильник', 'удали будильник', 'выключи будильник'),
    'sticker_add': ('напомни', 'поставь напоминание', 'добавь напоминание', 'установи напоминание'),
    'sticker_del': ('убери напоминание', 'удали напоминание'),
    'to_do_list_read': ('расскажи список дел', 'скажи список дел', 'какой список дел'),
    'to_do_list_add': ('добавь в список дел', 'запиши в список дел'),
    'to_do_list_del': ('удали из списка дел', 'убери из списка дел', 'вычеркни из списка дел'),
    'gen_password': ('сгенерируй пароль', 'придумай пароль', 'нужен пароль', 'дай пароль', 'придумать пароль'),
    'search_google': ('загугли', 'поищи в гугле', 'найди в гугле', 'поищи в гугл', 'найди в гугл'),
    'search_yandex': ('найди в яндексе', 'поищи в яндексе', 'найди в яндекс', 'поищи в яндекс'),
    'play_song': ('песню', 'музыку'),
    'play_radio': ('радио', ),
    'weather': ('погода', 'прогноз погоды', 'погоду'),
    'news': ('новости', ),
    'exchange_rate': ('курс валюты', 'курс валют'),
    'auto_clicker': ('включи автокликер', 'запусти автокликер', 'вруби автокликер'),
    'repeat': ('уву', 'кусь'),
    'start_app': ('запусти', 'включи'),
    'reset_settings': ('сброс настроек', 'сбросить настройки', 'сбрось настройки'),
    'translation': ('переведи',),
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


# Основа
o = bool(False)
while True:
    for cmd in speak_to_text():
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
        if o:
            break
    o = False
