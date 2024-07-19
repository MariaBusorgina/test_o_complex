## Сайт для просмотра прогноза погоды

### Описание
Django-проект для получения прогноза погоды в городе на ближайшее время.


### Установка
1. Клонировать репозиторий 
```bash
git clone https://github.com/MariaBusorgina/test_o_complex.git
```
2. Создать и активировать виртуальное окружение 
```bash
python -m venv venv
source venv/bin/activate
```
3. Перейти в каталог
```bash
cd project
```
4. Установить зависимости
```bash
pip install -r requirements.txt
```
5. Создать и применить миграции
```bash
python manage.py makemigrations
python manage.py migrate
```
6. Для восстановления данных из файла JSON выполнить (необходимо для реализации автозаполнения названия города):  
*** на данный момент настроена автозаполнение городов на букву "П"
```bash
python manage.py loaddata my_db.json
```
7. Запуск сервера
```bash
python manage.py runserver
```

**Доступные эндпоинты:**

GET http://127.0.0.1:8000/
Отображение главной страницы приложения, включая форму поиска погоды.

GET http://127.0.0.1:8000/weather/<str:city_name>/
Отображение подробной информации о погоде для указанного города.  
city_name — название города, для которого требуется получить прогноз погоды.

GET http://127.0.0.1:8000/city-search-count/
Получение количества поисков для каждого города. 

GET http://127.0.0.1:8000/search-history/
Отображение истории поиска городов, сохраненной в сессии. Включает список ранее введенных городов.

GET http://127.0.0.1:8000/city-autocomplete/
Автозаполнение для названия города на основе частичного ввода. Возвращает список городов, начинающихся с указанного префикса (используется для предложения возможных городов при вводе).  

