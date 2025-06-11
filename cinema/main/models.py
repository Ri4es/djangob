from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
import uuid

User = get_user_model()


class Hall(models.Model):
    code = models.CharField('Код зала', max_length=20, unique=True)
    name = models.CharField('Название', max_length=100)

    def __str__(self):
        return f'{self.code} – {self.name}'

    def update(self, **kwargs) -> 'Hall':
        for field, value in kwargs.items():
            setattr(self, field, value)
        self.save()
        return self

    def delete(self, **kwargs) -> tuple:
        return super().delete(**kwargs)

    class Meta:
        verbose_name = 'Зал'
        verbose_name_plural = 'Залы'


class Movie(models.Model):
    code = models.CharField('Код фильма', max_length=20, unique=True)
    title = models.CharField('Название', max_length=150)
    genre = models.CharField('Жанр', max_length=50, blank=True)
    rating = models.DecimalField('Рейтинг', max_digits=3, decimal_places=1, blank=True, null=True)
    duration = models.PositiveIntegerField('Длительность (мин)', blank=True, null=True)
    release_date = models.DateField('Дата выхода', blank=True, null=True)
    description = models.TextField('Описание', blank=True)

    def __str__(self):
        return f'{self.title} ({self.code})'

    def update(self, **kwargs) -> 'Movie':
        for field, value in kwargs.items():
            setattr(self, field, value)
        self.save()
        return self

    def delete(self, **kwargs) -> tuple:
        return super().delete(**kwargs)

    class Meta:
        verbose_name = 'Фильм'
        verbose_name_plural = 'Фильмы'


class Cinema(models.Model):
    code = models.CharField('Код кинотеатра', max_length=20, unique=True)
    city = models.CharField('Город', max_length=100)
    address = models.CharField('Адрес', max_length=255)

    def __str__(self):
        return f"{self.city} – {self.address}"

    def update(self, **kwargs) -> 'Cinema':
        for field, value in kwargs.items():
            setattr(self, field, value)
        self.save()
        return self

    def delete(self, **kwargs) -> tuple:
        return super().delete(**kwargs)

    class Meta:
        verbose_name = 'Кинотеатр'
        verbose_name_plural = 'Кинотеатры'


class Showtime(models.Model):
    code = models.CharField('Код сеанса', max_length=20, unique=True)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='showtimes')
    hall = models.ForeignKey(Hall, on_delete=models.CASCADE, related_name='showtimes')
    cinema = models.ForeignKey(
        Cinema,
        verbose_name='Кинотеатр',
        on_delete=models.CASCADE,
        related_name='showtimes',
        null=True
    )
    start_time = models.DateTimeField('Начало')
    end_time = models.DateTimeField('Окончание')
    available_seats = models.JSONField(
        default=list,
        help_text="Список доступных мест в формате JSON"
    )

    def __str__(self):
        return f'{self.code} – {self.movie.title} @ {self.start_time:%d.%m %H:%M}'

    def save(self, *args, **kwargs):
        if not self.pk:
            self.end_time = self.start_time + timedelta(minutes=self.movie.duration or 120)

        conflicts = Showtime.objects.filter(
            hall=self.hall,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time
        ).exclude(id=self.pk if self.pk else None)

        if conflicts.exists():
            raise ValidationError("Hall is already booked for this time")

        super().save(*args, **kwargs)

    def get_available_seats(self) -> list:
        booked_seats = set(Ticket.objects.filter(
            showtime=self
        ).values_list('seat', flat=True))
        return [seat for seat in self.available_seats if seat not in booked_seats]

    def init_seats(self, seats: list):
        self.available_seats = seats
        self.save()

    def update(self, **kwargs) -> 'Showtime':
        for field, value in kwargs.items():
            setattr(self, field, value)
        self.save()
        return self

    def delete(self, **kwargs) -> tuple:
        return super().delete(**kwargs)

    class Meta:
        verbose_name = 'Сеанс'
        verbose_name_plural = 'Сеансы'


class Ticket(models.Model):
    code = models.CharField('Код билета', max_length=20, unique=True)
    showtime = models.ForeignKey(Showtime, on_delete=models.CASCADE, related_name='tickets')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tickets')
    price = models.DecimalField('Стоимость', max_digits=8, decimal_places=2)
    seat = models.CharField('Место', max_length=10)
    is_booked = models.BooleanField('Забронирован', default=True)
    booking_date = models.DateTimeField('Дата брони', auto_now_add=True)

    def __str__(self):
        return f'Билет {self.code} – {self.showtime}'

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = f"T-{uuid.uuid4().hex[:6].upper()}"

        if Ticket.objects.filter(
                showtime=self.showtime,
                seat=self.seat
        ).exclude(id=self.pk).exists():
            raise ValidationError(f"Seat {self.seat} is already taken")

        super().save(*args, **kwargs)

    def update(self, **kwargs) -> 'Ticket':
        for field, value in kwargs.items():
            setattr(self, field, value)
        self.save()
        return self

    def delete(self, **kwargs) -> tuple:
        return super().delete(**kwargs)

    class Meta:
        verbose_name = 'Билет'
        verbose_name_plural = 'Билеты'