from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
import uuid

User = get_user_model()


class HallManager(models.Manager):
    def create_hall(self, code: str, name: str) -> 'Hall':
        return self.create(code=code, name=name)

    def get_hall(self, hall_id: int = None, code: str = None) -> 'Hall':
        if hall_id:
            return self.filter(id=hall_id).first()
        if code:
            return self.filter(code=code).first()
        return None


class Hall(models.Model):
    code = models.CharField('Код зала', max_length=20, unique=True)
    name = models.CharField('Название', max_length=100)

    objects = HallManager()

    def update_hall(self, **kwargs) -> 'Hall':
        for field, value in kwargs.items():
            setattr(self, field, value)
        self.save()
        return self

    def delete_hall(self) -> bool:
        self.delete()
        return True

    def __str__(self):
        return f'{self.code} – {self.name}'

    class Meta:
        verbose_name = 'Зал'
        verbose_name_plural = 'Залы'


class MovieManager(models.Manager):
    def create_movie(self, code: str, title: str, **kwargs) -> 'Movie':
        return self.create(code=code, title=title, **kwargs)

    def get_movie(self, movie_id: int = None, code: str = None) -> 'Movie':
        if movie_id:
            return self.filter(id=movie_id).first()
        if code:
            return self.filter(code=code).first()
        return None

    def get_movies_by_genre(self, genre: str) -> list:
        return self.filter(genre__icontains=genre)


class Movie(models.Model):
    code = models.CharField('Код фильма', max_length=20, unique=True)
    title = models.CharField('Название', max_length=150)
    genre = models.CharField('Жанр', max_length=50, blank=True)
    rating = models.DecimalField('Рейтинг', max_digits=3, decimal_places=1, blank=True, null=True)
    duration = models.PositiveIntegerField('Длительность (мин)', blank=True, null=True)
    release_date = models.DateField('Дата выхода', blank=True, null=True)
    description = models.TextField('Описание', blank=True)

    objects = MovieManager()

    def update_movie(self, **kwargs) -> 'Movie':
        for field, value in kwargs.items():
            setattr(self, field, value)
        self.save()
        return self

    def delete_movie(self) -> bool:
        self.delete()
        return True

    def __str__(self):
        return f'{self.title} ({self.code})'

    class Meta:
        verbose_name = 'Фильм'
        verbose_name_plural = 'Фильмы'


class CinemaManager(models.Manager):
    def create_cinema(self, code: str, city: str, address: str) -> 'Cinema':
        return self.create(code=code, city=city, address=address)

    def get_cinema(self, cinema_id: int = None, code: str = None) -> 'Cinema':
        if cinema_id:
            return self.filter(id=cinema_id).first()
        if code:
            return self.filter(code=code).first()
        return None

    def get_cinemas_by_city(self, city: str) -> list:
        return self.filter(city__iexact=city)


class Cinema(models.Model):
    code = models.CharField('Код кинотеатра', max_length=20, unique=True)
    city = models.CharField('Город', max_length=100)
    address = models.CharField('Адрес', max_length=255)

    objects = CinemaManager()

    def update_cinema(self, **kwargs) -> 'Cinema':
        for field, value in kwargs.items():
            setattr(self, field, value)
        self.save()
        return self

    def delete_cinema(self) -> bool:
        self.delete()
        return True

    def __str__(self):
        return f"{self.city} – {self.address}"

    class Meta:
        verbose_name = 'Кинотеатр'
        verbose_name_plural = 'Кинотеатры'



class ShowtimeManager(models.Manager):
    @transaction.atomic
    def create_showtime(
            self,
            code: str,
            movie_id: int,
            hall_id: int,
            cinema_id: int,
            start_time: datetime
    ) -> 'Showtime':
        movie = Movie.objects.get_movie(movie_id=movie_id)
        hall = Hall.objects.get_hall(hall_id=hall_id)
        cinema = Cinema.objects.get_cinema(cinema_id=cinema_id)

        if not all([movie, hall, cinema]):
            raise ValidationError("Invalid movie, hall or cinema ID")

        end_time = start_time + timedelta(minutes=movie.duration or 120)

        if self.filter(
                hall=hall,
                start_time__lt=end_time,
                end_time__gt=start_time
        ).exists():
            raise ValidationError("Hall is already booked for this time")

        return self.create(
            code=code,
            movie=movie,
            hall=hall,
            cinema=cinema,
            start_time=start_time,
            end_time=end_time
        )

    def get_showtime(self, showtime_id: int = None, code: str = None) -> 'Showtime':
        if showtime_id:
            return self.filter(id=showtime_id).first()
        if code:
            return self.filter(code=code).first()
        return None

    def get_showtimes_by_date(self, date: datetime.date) -> list:
        start_of_day = datetime.combine(date, datetime.min.time())
        end_of_day = start_of_day + timedelta(days=1)
        return self.filter(
            start_time__range=(start_of_day, end_of_day)
        ).select_related('movie', 'hall', 'cinema')

    def get_showtimes_by_cinema(self, cinema_id: int) -> list:
        return self.filter(cinema_id=cinema_id).select_related('movie')


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

    objects = ShowtimeManager()

    def get_available_seats(self) -> list:
        booked_seats = set(Ticket.objects.filter(
            showtime=self
        ).values_list('seat', flat=True))

        return [seat for seat in self.available_seats if seat not in booked_seats]

    def init_seats(self, seats: list):
        self.available_seats = seats
        self.save()

    @transaction.atomic
    def update_showtime(self, **kwargs) -> 'Showtime':
        movie = kwargs.get('movie', self.movie)
        start_time = kwargs.get('start_time', self.start_time)
        end_time = start_time + timedelta(minutes=movie.duration or 120)

        if 'hall' in kwargs or 'start_time' in kwargs:
            hall = kwargs.get('hall', self.hall)
            if Showtime.objects.filter(
                    hall=hall,
                    start_time__lt=end_time,
                    end_time__gt=start_time
            ).exclude(id=self.id).exists():
                raise ValidationError("Time conflict with existing showtime")

        kwargs['end_time'] = end_time
        for field, value in kwargs.items():
            setattr(self, field, value)
        self.save()
        return self

    def delete_showtime(self) -> bool:
        self.delete()
        return True

    def __str__(self):
        return f'{self.code} – {self.movie.title} @ {self.start_time:%d.%m %H:%M}'

    class Meta:
        verbose_name = 'Сеанс'
        verbose_name_plural = 'Сеансы'


# Кастомный менеджер для Ticket
class TicketManager(models.Manager):
    @transaction.atomic
    def create_ticket(
            self,
            showtime_id: int,
            user_id: int,
            price: float,
            seat: str
    ) -> 'Ticket':
        showtime = Showtime.objects.get_showtime(showtime_id=showtime_id)
        if not showtime:
            raise ValidationError("Showtime not found")

        user = User.objects.filter(id=user_id).first() if user_id else None
        ticket_code = f"T-{uuid.uuid4().hex[:6].upper()}"

        if self.filter(showtime=showtime, seat=seat).exists():
            raise ValidationError(f"Seat {seat} is already taken")

        return self.create(
            code=ticket_code,
            showtime=showtime,
            user=user,
            price=price,
            seat=seat
        )

    def get_ticket(self, ticket_id: int = None, code: str = None) -> 'Ticket':
        if ticket_id:
            return self.filter(id=ticket_id).first()
        if code:
            return self.filter(code=code).first()
        return None

    def get_tickets_by_user(self, user_id: int) -> list:
        return self.filter(user_id=user_id).select_related('showtime')

    def get_tickets_by_showtime(self, showtime_id: int) -> list:
        return self.filter(showtime_id=showtime_id)


class Ticket(models.Model):
    code = models.CharField('Код билета', max_length=20, unique=True)
    showtime = models.ForeignKey(Showtime, on_delete=models.CASCADE, related_name='tickets')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tickets')
    price = models.DecimalField('Стоимость', max_digits=8, decimal_places=2)
    seat = models.CharField('Место', max_length=10)
    is_booked = models.BooleanField('Забронирован', default=True)
    booking_date = models.DateTimeField('Дата брони', auto_now_add=True)

    objects = TicketManager()

    @transaction.atomic
    def update_ticket(self, **kwargs) -> 'Ticket':
        if 'seat' in kwargs:
            if Ticket.objects.filter(
                    showtime=self.showtime,
                    seat=kwargs['seat']
            ).exclude(id=self.id).exists():
                raise ValidationError(f"Seat {kwargs['seat']} is already taken")

        for field, value in kwargs.items():
            setattr(self, field, value)
        self.save()
        return self

    def delete_ticket(self) -> bool:
        self.delete()
        return True

    def __str__(self):
        return f'Билет {self.code} – {self.showtime}'

    class Meta:
        verbose_name = 'Билет'
        verbose_name_plural = 'Билеты'