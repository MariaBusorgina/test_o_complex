import calendar
from datetime import datetime

from django.shortcuts import render
from django.http import JsonResponse
import requests
from geopy.geocoders import Nominatim

from weather_app.models import CitySearch, City


def format_time(time_str):
    """
    Функция для преобразования строки времени в формат строки,
    содержащую день недели на русском языке и время в формате "часы:минуты".
    """
    dt = datetime.fromisoformat(time_str)
    weekday_name = calendar.day_name[dt.weekday()]

    weekday = {
        'Monday': 'Понедельник',
        'Tuesday': 'Вторник',
        'Wednesday': 'Среда',
        'Thursday': 'Четверг',
        'Friday': 'Пятница',
        'Saturday': 'Суббота',
        'Sunday': 'Воскресенье',
    }[weekday_name]

    formatted_time = dt.strftime('%H:%M')

    return f'{weekday} {formatted_time}'


def get_weather(lat, lon):
    """
    Функция для получение показателей текущей погоды и дневного прогноза
    """
    url = 'https://api.open-meteo.com/v1/forecast'
    params = {
        'latitude': lat,
        'longitude': lon,
        'current_weather': 'true',
        'timezone': 'auto',
        'daily': 'temperature_2m_max,temperature_2m_min,weather_code,precipitation_probability_max',
        'windspeed_unit': 'ms'
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    return None


def get_coordinates(city):
    """
    Функция для получения координат города (широты и долготы) с использованием Nominatim API.
    """
    geolocator = Nominatim(user_agent="weather_app")
    try:
        location = geolocator.geocode(city, exactly_one=True, timeout=10)
        print(location.raw)
        if location:
            if any(type_keyword in location.raw['type'] for type_keyword in ['city', 'town', 'administrative']):
                city_name = location.raw['display_name'].split(',')[0].strip().casefold()

                if city.casefold().replace('ё', 'е').replace('й', 'и') == city_name.replace('ё', 'е').replace('й', 'и'):
                    return location.latitude, location.longitude
                else:
                    parts = city_name.split()
                    for part in parts:
                        if city.casefold() == part:
                            return location.latitude, location.longitude
            else:
                return None, None
    except Exception as e:
        return None, None


def process_weather_request(request, city):
    """
    Обрабатывает запрос на получение данных о погоде для указанного города.
    """
    lat, lon = get_coordinates(city)
    if lat and lon:
        weather_data = get_weather(lat, lon)

        if weather_data:
            formatted_time = format_time(weather_data['current_weather']['time'])

            # Сохраняем город в историю поиска в сессии
            if request.method == 'POST':
                searches = request.session.get('city_searches', [])
                city = city.title()
                searches.append(city)
                request.session['city_searches'] = list(set(searches))

                # Обновляем или создаем запись в базе данных для глобальной статистики
                city_search, created = CitySearch.objects.get_or_create(city=city)
                city_search.search_count += 1
                city_search.save()

            return render(request, 'weather_app/index.html', {
                'weather_data': weather_data,
                'city_searches': request.session.get('city_searches', []),
                'formatted_time': formatted_time,
                'city': city
            })
        else:
            error_message = f'Прогноз погоды для города "{city}" не найден.'
            return render(request, 'weather_app/index.html', {
                'error_message': error_message,
                'city_searches': request.session.get('city_searches', [])
            })
    else:
        error_message = f"Город {city} не найден."
        return render(request, 'weather_app/index.html', {
            'error_message': error_message,
            'city_searches': request.session.get('city_searches', [])
        })


def index(request):
    """
    Обрабатывает запросы на главную страницу веб-приложения погоды.

    При POST запросе: Обрабатывает запрос на поиск погоды по введенному городу.
    При GET запросе: Показывает страницу поиска.
    """
    if request.method == 'POST':
        city = request.POST.get('city')
        return process_weather_request(request, city)

    return render(request, 'weather_app/index.html', {
        'city_searches': request.session.get('city_searches', [])
    })


def weather_detail(request, city_name):
    """
    Обрабатывает запросы для отображения данных о погоде для указанного города.
    """
    return process_weather_request(request, city_name)


def city_search_count_api(request):
    """Получение количества просмотра каждого города"""
    search_counts = {entry.city: entry.search_count for entry in CitySearch.objects.all()}
    sorted_search_counts = dict(sorted(search_counts.items(), key=lambda item: (-item[1], item[0])))

    return JsonResponse(sorted_search_counts, json_dumps_params={'ensure_ascii': False})


def search_history(request):
    """Просмотр истории поиска"""
    searches = request.session.get('city_searches', [])
    return JsonResponse(searches, json_dumps_params={'ensure_ascii': False}, safe=False)


def city_autocomplete(request):
    """
    Функция для обработки запроса на автозаполнение названия города
    """
    if 'term' in request.GET:
        qs = City.objects.filter(name__istartswith=request.GET.get('term'))
        cities = list(qs.values_list('name', flat=True))
        return JsonResponse(cities, safe=False)
    return JsonResponse([], safe=False)
