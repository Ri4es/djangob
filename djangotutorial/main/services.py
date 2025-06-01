# main/services.py
from .models import Hall, Movie, Cinema, Showtime, Ticket
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.contrib.auth import get_user_model
from django.db import transaction
from datetime import datetime, timedelta
import uuid

User = get_user_model()


class HallService:
    @staticmethod
    def create_hall(code: str, name: str) -> Hall:
        return Hall.objects.create(code=code, name=name)

    @staticmethod
    def get_hall_by_id(hall_id: int) -> Hall:
        try:
            return Hall.objects.get(id=hall_id)
        except ObjectDoesNotExist:
            return None

    @staticmethod
    def get_hall_by_code(code: str) -> Hall:
        try:
            return Hall.objects.get(code=code)
        except ObjectDoesNotExist:
            return None

    @staticmethod
    def update_hall(hall_id: int, **kwargs) -> Hall:
        hall = HallService.get_hall_by_id(hall_id)
        if hall:
            for field, value in kwargs.items():
                setattr(hall, field, value)
            hall.save()
        return hall

    @staticmethod
    def delete_hall(hall_id: int) -> bool:
        hall = HallService.get_hall_by_id(hall_id)
        if hall:
            hall.delete()
            return True
        return False


class MovieService:
    @staticmethod
    def create_movie(
            code: str,
            title: str,
            genre: str = "",
            rating: float = None,
            duration: int = None,
            release_date: datetime.date = None,
            description: str = ""
    ) -> Movie:
        return Movie.objects.create(
            code=code,
            title=title,
            genre=genre,
            rating=rating,
            duration=duration,
            release_date=release_date,
            description=description
        )

    @staticmethod
    def get_movie_by_id(movie_id: int) -> Movie:
        try:
            return Movie.objects.get(id=movie_id)
        except ObjectDoesNotExist:
            return None

    @staticmethod
    def get_movie_by_code(code: str) -> Movie:
        try:
            return Movie.objects.get(code=code)
        except ObjectDoesNotExist:
            return None

    @staticmethod
    def get_movies_by_genre(genre: str) -> list:
        return Movie.objects.filter(genre__icontains=genre)

    @staticmethod
    def update_movie(movie_id: int, **kwargs) -> Movie:
        movie = MovieService.get_movie_by_id(movie_id)
        if movie:
            for field, value in kwargs.items():
                setattr(movie, field, value)
            movie.save()
        return movie

    @staticmethod
    def delete_movie(movie_id: int) -> bool:
        movie = MovieService.get_movie_by_id(movie_id)
        if movie:
            movie.delete()
            return True
        return False


class CinemaService:
    @staticmethod
    def create_cinema(code: str, city: str, address: str) -> Cinema:
        return Cinema.objects.create(code=code, city=city, address=address)

    @staticmethod
    def get_cinema_by_id(cinema_id: int) -> Cinema:
        try:
            return Cinema.objects.get(id=cinema_id)
        except ObjectDoesNotExist:
            return None

    @staticmethod
    def get_cinema_by_code(code: str) -> Cinema:
        try:
            return Cinema.objects.get(code=code)
        except ObjectDoesNotExist:
            return None

    @staticmethod
    def get_cinemas_by_city(city: str) -> list:
        return Cinema.objects.filter(city__iexact=city)

    @staticmethod
    def update_cinema(cinema_id: int, **kwargs) -> Cinema:
        cinema = CinemaService.get_cinema_by_id(cinema_id)
        if cinema:
            for field, value in kwargs.items():
                setattr(cinema, field, value)
            cinema.save()
        return cinema

    @staticmethod
    def delete_cinema(cinema_id: int) -> bool:
        cinema = CinemaService.get_cinema_by_id(cinema_id)
        if cinema:
            cinema.delete()
            return True
        return False


class ShowtimeService:
    @staticmethod
    @transaction.atomic
    def create_showtime(
            code: str,
            movie_id: int,
            hall_id: int,
            cinema_id: int,
            start_time: datetime
    ) -> Showtime:
        movie = MovieService.get_movie_by_id(movie_id)
        hall = HallService.get_hall_by_id(hall_id)
        cinema = CinemaService.get_cinema_by_id(cinema_id)

        if not movie:
            raise ValidationError(f"Фильм с ID {movie_id} не найден")
        if not hall:
            raise ValidationError(f"Зал с ID {hall_id} не найден")
        if not cinema:
            raise ValidationError(f"Кинотеатр с ID {cinema_id} не найден")


        end_time = start_time + timedelta(minutes=movie.duration or 120)
        overlapping_showtimes = Showtime.objects.filter(
            hall=hall,
            start_time__lt=end_time,
            end_time__gt=start_time
        )

        if overlapping_showtimes.exists():
            raise ValidationError("Зал уже занят в это время")

        return Showtime.objects.create(
            code=code,
            movie=movie,
            hall=hall,
            cinema=cinema,
            start_time=start_time,
            end_time=end_time
        )

    @staticmethod
    def get_available_seats(showtime_id: int) -> list:
        showtime = ShowtimeService.get_showtime_by_id(showtime_id)
        if not showtime:
            return []

        # Получаем занятые места
        booked_seats = Ticket.objects.filter(
            showtime=showtime
        ).values_list('seat', flat=True)

        # Фильтруем доступные места
        return [seat for seat in showtime.available_seats if seat not in booked_seats]

    @staticmethod
    def init_seats(showtime_id: int, seats: list):
        showtime = ShowtimeService.get_showtime_by_id(showtime_id)
        if showtime:
            showtime.available_seats = seats
            showtime.save()

    @staticmethod
    def get_showtime_by_id(showtime_id: int) -> Showtime:
        try:
            return Showtime.objects.get(id=showtime_id)
        except ObjectDoesNotExist:
            return None

    @staticmethod
    def get_showtime_by_code(code: str) -> Showtime:
        try:
            return Showtime.objects.get(code=code)
        except ObjectDoesNotExist:
            return None

    @staticmethod
    def get_showtimes_by_date(date: datetime.date) -> list:
        start_of_day = datetime.combine(date, datetime.min.time())
        end_of_day = start_of_day + timedelta(days=1)
        return Showtime.objects.filter(
            start_time__range=(start_of_day, end_of_day)
        ).select_related('movie', 'hall', 'cinema')

    @staticmethod
    def get_showtimes_by_cinema(cinema_id: int) -> list:
        return Showtime.objects.filter(cinema_id=cinema_id).select_related('movie')

    @staticmethod
    def update_showtime(showtime_id: int, **kwargs) -> Showtime:
        showtime = ShowtimeService.get_showtime_by_id(showtime_id)
        if not showtime:
            return None


        movie = kwargs.get('movie', showtime.movie)
        start_time = kwargs.get('start_time', showtime.start_time)


        if 'movie' in kwargs or 'start_time' in kwargs:
            duration = timedelta(minutes=movie.duration) if movie.duration else timedelta(hours=2)
            kwargs['end_time'] = start_time + duration


        if 'hall' in kwargs or 'start_time' in kwargs:
            hall = kwargs.get('hall', showtime.hall)
            end_time = kwargs.get('end_time', showtime.end_time)

            overlapping = Showtime.objects.filter(
                hall=hall,
                start_time__lt=end_time,
                end_time__gt=start_time
            ).exclude(id=showtime_id)

            if overlapping.exists():
                raise ValidationError("Обнаружен конфликт времени сеанса")


        for field, value in kwargs.items():
            setattr(showtime, field, value)

        showtime.save()
        return showtime

    @staticmethod
    def delete_showtime(showtime_id: int) -> bool:
        showtime = ShowtimeService.get_showtime_by_id(showtime_id)
        if showtime:
            showtime.delete()
            return True
        return False


class TicketService:
    @staticmethod
    @transaction.atomic
    def create_ticket(
            code: str,
            showtime_id: int,
            user_id: int,
            price: float,
            seat: str
    ) -> Ticket:
        showtime = ShowtimeService.get_showtime_by_id(showtime_id)
        if not showtime:
            raise ValidationError(f"Сеанс с ID {showtime_id} не найден")

        user = User.objects.get(id=user_id) if user_id else None


        existing_ticket = Ticket.objects.filter(
            showtime=showtime,
            seat=seat
        ).exists()

        if existing_ticket:
            raise ValidationError(f"Место {seat} уже занято")

        return Ticket.objects.create(
            code=code,
            showtime=showtime,
            user=user,
            price=price,
            seat=seat
        )

    class TicketService:
        @staticmethod
        @transaction.atomic
        def book_ticket(
                showtime_id: int,
                user_id: int,
                seat: str
        ) -> Ticket:
            showtime = ShowtimeService.get_showtime_by_id(showtime_id)
            if not showtime:
                raise ValidationError(f"Сеанс с ID {showtime_id} не найден")

            user = User.objects.get(id=user_id) if user_id else None

            # Автоматическая генерация уникального кода
            code = f"T-{uuid.uuid4().hex[:6].upper()}"

            # Проверка доступности места
            existing_ticket = Ticket.objects.filter(
                showtime=showtime,
                seat=seat
            ).exists()

            if existing_ticket:
                raise ValidationError(f"Место {seat} уже занято")

            return Ticket.objects.create(
                code=code,
                showtime=showtime,
                user=user,
                price=0,  # Бесплатное бронирование
                seat=seat,
                is_booked=True
            )

    @staticmethod
    def get_ticket_by_id(ticket_id: int) -> Ticket:
        try:
            return Ticket.objects.get(id=ticket_id)
        except ObjectDoesNotExist:
            return None

    @staticmethod
    def get_ticket_by_code(code: str) -> Ticket:
        try:
            return Ticket.objects.get(code=code)
        except ObjectDoesNotExist:
            return None

    @staticmethod
    def get_tickets_by_user(user_id: int) -> list:
        return Ticket.objects.filter(user_id=user_id).select_related('showtime')

    @staticmethod
    def get_tickets_by_showtime(showtime_id: int) -> list:
        return Ticket.objects.filter(showtime_id=showtime_id)

    @staticmethod
    def update_ticket(ticket_id: int, **kwargs) -> Ticket:
        ticket = TicketService.get_ticket_by_id(ticket_id)
        if not ticket:
            return None


        if 'seat' in kwargs:
            existing = Ticket.objects.filter(
                showtime=ticket.showtime,
                seat=kwargs['seat']
            ).exclude(id=ticket_id).exists()

            if existing:
                raise ValidationError(f"Место {kwargs['seat']} уже занято")


        for field, value in kwargs.items():
            setattr(ticket, field, value)

        ticket.save()
        return ticket

    @staticmethod
    def delete_ticket(ticket_id: int) -> bool:
        ticket = TicketService.get_ticket_by_id(ticket_id)
        if ticket:
            ticket.delete()
            return True
        return False

    def create_ticket(
            showtime_id: int,
            user_id: int,
            price: float,
            seat: str
    ) -> Ticket:
        showtime = ShowtimeService.get_showtime_by_id(showtime_id)
        if not showtime:
            raise ValidationError(f"Сеанс с ID {showtime_id} не найден")

        user = User.objects.get(id=user_id) if user_id else None

        # Автоматическая генерация уникального кода
        code = f"TICKET-{uuid.uuid4().hex[:8].upper()}"

        # Проверка доступности места
        existing_ticket = Ticket.objects.filter(
            showtime=showtime,
            seat=seat
        ).exists()

        if existing_ticket:
            raise ValidationError(f"Место {seat} уже занято")

        return Ticket.objects.create(
            code=code,  # Используем сгенерированный код
            showtime=showtime,
            user=user,
            price=price,
            seat=seat)