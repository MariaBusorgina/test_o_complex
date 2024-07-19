from django.db import models


class CitySearch(models.Model):
    """Модель для хранения статистики запросов"""
    city = models.CharField(max_length=50)
    search_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.city


class City(models.Model):
    name = models.CharField(max_length=100, unique=True, db_index=True)

    def __str__(self):
        return self.name