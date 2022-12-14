<img src="/icon.png" width="300">
<h1>Fula - голосовой помощник</h1>
<h2>Основа голосового помощника может работать в автономном режиме (без интернета)</h2>
<h3 id="links">Содержание</h3>
<ul>
    <li><a href="#links">Содержание</a></li>
    <li><a href="#accuracy-stt">Если вас не устаривает точность STT (точности распознавания речи)</a></li>
    <li><a href="#how-to-install">Как установить себе Фулу</a></li>
    <li><a href="#functions">Фунции</a></li>
    <li><a href="#property">Характеристики</a></li>
    <li><a href="#all-trigger-words">Все слова "тригеры"</a></li>
</ul>
<h4 id="accuracy-stt">Если вас не устаривает точность STT (точности распознавания речи) то:</h4>
<ol>
    <li>Скачайте большую модель</li>
    <li>Перенесите папу модели в папку с Fula</li>
    <li>Измените параметр "model = Model("small_model")" на "model = Model("model")"</li>
</ol>
<div>Только учитывайте то что для маленькой модели требуется около 100МБ оперативной памяти и памяти на жёстком диске, а для большой модели требуется около 5ГБ оперативной памяти и памяти на жёстком диске</div>
<div>!!! И это только для одного голосового синтезатора STT (vosk) !!!</div>
<h3 id="how-to-install">Как установить себе Фулу</h3>
<div>Если вы это читаете то разработчик просматриваемого вами голосового помощника до сих пор не написал сайт с установщиками скомпилированной Фулы</div>
<div>То что будет написанно дальше в этом пункте будет для тех кто очень сильно заинтересован проектом и хочет раньше времени увидеть что это за голосовой помощник</div>
<div>Для преждевременного использования голосового помощника есть 2 способа</div>
<ul>
    <li>Вариант 1 (Для опытных или умеющих гуглить)<br>Если хотите то можете попробовать скомпилировать весь проект</li>
    <li>Вариант 2<br>Установить Python и запустить Fula.py с его помощью (Если появилась ошибка связанная с библиотеками, уточните версию библиотеки используемой в коде (в Fula.py) голосовом помощнике)</li>
</ul>
<h3 id="functions">Фунции:</h3>
<ul>
    <li>Прогноз погоды
        <br>
        <i>Примечание:
        <ul>
            <li>при отсутствии в запросе нужного города местоположение будет определяться автоматически через IP что является не очень точным методом если вы находитесь не в крупном населённом пункте</li>
        </ul>
        </i>
    </li>
    <li>Поиск в Яндексе</li>
    <li>Поиск в Google
        <br>
        <i>Примечание:
        <ul>
            <li>Слово "Загугли" STT не распознаёт</li>
        </ul>
        </i>
    </li>
    <li>Генератор паролей
        <br>
        <i>Примечание:
        <ul>
            <li>После генерации пароля он будет помещён в буфер обмена</li>
        </ul>
        </i>
    </li>
    <li>Время сейчас</li>
    <li>Анекдоты</li>
    <li>Сброс настроек</li>
    <li>Озвучивание нагрузки на систему
        <br>
        <i>Примечание:
        <ul>
            <li>Нагрузка на процессор (%)</li>
            <li>Нагрузка на оперативную память (%)</li>
        </ul>
        </i>
    </li>
    <li>Озвучивание подробной нагрузки на систему
        <br>
        <i>Примечание:
        <ul>
            <li>Нагрузка на процессор (%)</li>
            <li>Количество ядер</li>
            <li>Количество потоков</li>
            <li>Нагрузка на оперативную память (%)</li>
            <li>Сколько всего памяти в ОЗУ (ГБ)</li>
            <li>Сколько всего памяти занято в ОЗУ (ГБ)</li>
            <li>Сколько всего памяти свободно в ОЗУ (ГБ)</li>
            <div>Всё последующее будет расписано для каждого вашего локального диска:</div>
            <li>Сколько всего памяти на устройстве (%)</li>
            <li>Сколько всего памяти на устройстве (ГБ)</li>
            <li>Сколько всего занятой памяти на устройстве (ГБ)</li>
            <li>Сколько всего свободной памяти на устройстве (ГБ)</li>
        </ul>
        </i>    
    </li>
    <li>Подбрасывание монетки (Орёл или решка)</li>
    <li>"Голосовые кнопки"
        <br>
        <i>Список:
        <ul>
            <li>Повышение громкости на компьютере</li>
            <li>Понижение громкости на компьютере</li>
            <li>Переключение музыки/песни/видео на следующее</li>
            <li>Переключение музыки/песни/видео на предыдущее</li>
            <li>Пауза</li>
            <li>Выключение звука на компьютере</li>
        </ul>
        </i>
    </li>
    <li>Перевод скопированного
        <br>
        <i>Примечание
        <ul>
            <li>При желании скопировать переведённое добавьте в сказанное вами "скопируй в буфер обмена"</li>
        </ul>
        </i>
    </li>
    <li>Разговорник V0.1_1
        <br>
        <i>Примечание:
        <ul>
            <li>к словам которые относятся к разговорнику можно отнести:<br>
            "Дополнительная Информация", "Ты Кто", "Кто Ты", "Кто Тебя Создал", "Кто Твой Создатель", "Как Зовут Твоего Создателя", "Расскажи О Себе", "Как Тебя Зовут", "Привет", "Хай", "Хэйоу", "Здравствуй", "Здравствуйте", "Шутка", "Шутку", "Анекдот", "Анекдоты", "Пошути", "Что Ты Умеешь", "Что Тебе Нравится", "Что Ты Любишь", "Чем Ты Увлекаешься", "Что Тебе Не Нравится", "Что Ты Ненавидишь", "Что Ты Не Любишь", "Кого Ты Ненавидишь", "Кого Ты Не Любишь", "Кто Тебе Не Нравится", "Привет Алиса", "Привет Маруся", "Маруся", "Где Ты Живёшь", "Где Ты Сейчас Живёшь", "Какое Твоё Месторасположение", "Какая Твоя Геолокация", "Где Ты", "Какое Твоё Любимое Устройство", "Где Тебе Нравится Жить", "Какая Твоя Любимая Игра", "Во Что Ты Любишь Играть", "Ня", "Дежавю"
            </li>
        </ul>
        </i>
    </li>
</ul>
<h4 id="property">Характеристики</h4>
<div>Используемые голосовые синтезатор речи:</div>
<ul>
    <li>TTS (text to speech) - <a href="https://github.com/snakers4/silero-models">Silero</a></li>
    <li>STT (speech to text) - <a href="https://github.com/alphacep/vosk-api">vosk</a></li>
</ul>
<table>
    <tr>
        <th>Текущая версия</th>
        <th colspan="2">Версия - 0.0.3</th>
    </tr>
    <tr>
        <th rowspan="3">Минимальные требования</th>
        <th colspan="2">Нормальный центральный процессор</th>
    </tr>
    <tr>
        <th colspan="2">Наличие микрофона</th>
    </tr>
    <tr>
        <th colspan="2">Динамики или наушники</th>
    </tr>
    <tr>
        <th rowspan="2">Модели от vosk<br>и их требования<br>(STT)</th>
        <th><a href="https://alphacephei.com/vosk/models/vosk-model-small-ru-0.22.zip">small_model<br>(Стандартная)</a></th>
        <th>100МБ ОЗУ</th>
    </tr>
    <tr>
        <th><a href="https://alphacephei.com/vosk/models/vosk-model-ru-0.22.zip">model</a></th>
        <th>5ГБ ОЗУ</th>
    </tr>
</table>
<h5 id="all-trigger-words">Все слова "тригеры":</h5>
<div>"Который Час", "Сколько Времени", "Сколько Время", "Часы", "Что На Часах", "Текущее Время", "Сгенерируй Пароль", "Придумай Пароль", "Нужен Пароль", "Дай Пароль", "Придумать Пароль", "Сгенерировать Пароль", "Загугли", "Поищи В Гугле", "Найди В Гугле", "Поищи В Гугл", "Найди В Гугл", "Найди В Яндексе", "Поищи В Яндексе", "Найди В Яндекс", "Поищи В Яндекс", "Погода", "Прогноз Погоды", "Погоду", "Сброс Настроек", "Сбросить Настройки", "Сбрось Настройки", "Переведи", "Паузу", "Пауза", "Паузы", "Пуск", "Следующая Песня", "Следующее Видео", "Следующая Музыка", "Следующую Песню", "Следующую Музыку", "Предыдущая Песня", "Предыдущее Видео", "Предыдущая Музыка", "Предыдущую Песню", "Предыдущую Музыку", "Повысь Громкость", "Громче", "Громкость Повыше", "Понизь Громкость", "Тише", "Громкость Пониже", "Выключи Звук", "Выруби Звук", "Включи Звук", "Вруби Звук", "Полный Отчёт О Системе", "Подробный Отчёт О Системе", "Отчёт О Системе", "Нагрузка На Систему", "Орёл Или Решка", "Подбрось Монетку", "Дополнительная Информация", "Ты Кто", "Кто Ты", "Кто Тебя Создал", "Кто Твой Создатель", "Как Зовут Твоего Создателя", "Расскажи О Себе", "Как Тебя Зовут", "Привет", "Хай", "Хэйоу", "Здравствуй", "Здравствуйте", "Шутка", "Шутку", "Анекдот", "Анекдоты", "Пошути", "Что Ты Умеешь", "Что Тебе Нравится", "Что Ты Любишь", "Чем Ты Увлекаешься", "Что Тебе Не Нравится", "Что Ты Ненавидишь", "Что Ты Не Любишь", "Кого Ты Ненавидишь", "Кого Ты Не Любишь", "Кто Тебе Не Нравится", "Привет Алиса", "Привет Маруся", "Маруся", "Где Ты Живёшь", "Где Ты Сейчас Живёшь", "Какое Твоё Месторасположение", "Какая Твоя Геолокация", "Где Ты", "Какое Твоё Любимое Устройство", "Где Тебе Нравится Жить", "Какая Твоя Любимая Игра", "Во Что Ты Любишь Играть", "Ня", "Не", "Уву", "Дежавю"</div>