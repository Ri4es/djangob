from django.db import models
from django.conf import settings

# Create your models here.
class Hall(models.Model):
    code = models.CharField('Код зала', max_length=20, unique=True)
    name = models.CharField('Название', max_length=100)

    def __str__(self):
        return f'{self.code} – {self.name}'

    class Meta:
        verbose_name = 'Зал'
        verbose_name_plural = 'Залы'


class Movie(models.Model):
    code        = models.CharField('Код фильма', max_length=20, unique=True)
    title       = models.CharField('Название', max_length=150)
    genre       = models.CharField('Жанр', max_length=50, blank=True)
    rating      = models.DecimalField('Рейтинг', max_digits=3, decimal_places=1, blank=True, null=True)
    duration    = models.PositiveIntegerField('Длительность (мин)', blank=True, null=True)
    release_date = models.DateField('Дата выхода', blank=True, null=True)
    description = models.TextField('Описание', blank=True)

    def __str__(self):
        return f'{self.title} ({self.code})'

    class Meta:
        verbose_name = 'Фильм'
        verbose_name_plural = 'Фильмы'


class Showtime(models.Model):
    code       = models.CharField('Код сеанса', max_length=20, unique=True)
    movie      = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='showtimes')
    hall       = models.ForeignKey(Hall,  on_delete=models.CASCADE, related_name='showtimes')
    start_time = models.DateTimeField('Начало')
    end_time   = models.DateTimeField('Окончание')

    def __str__(self):
        return f'{self.code} – {self.movie.title} @ {self.start_time:%d.%m %H:%M}'

    class Meta:
        verbose_name = 'Сеанс'
        verbose_name_plural = 'Сеансы'


class Ticket(models.Model):
    code      = models.CharField('Код билета', max_length=20, unique=True)
    showtime  = models.ForeignKey(Showtime, on_delete=models.CASCADE, related_name='tickets')
    user      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tickets')
    price     = models.DecimalField('Стоимость', max_digits=8, decimal_places=2)
    seat      = models.CharField('Место', max_length=10)

    def __str__(self):
        return f'Билет {self.code} – {self.showtime}'

    class Meta:
        verbose_name = 'Билет'
        verbose_name_plural = 'Билеты'