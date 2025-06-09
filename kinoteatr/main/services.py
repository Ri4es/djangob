from .models import Hall, Movie, Cinema, Showtime, Ticket

class hall_operations:
    @classmethod
    def create_hall(cls, code: str, name: str) -> Hall:
        return Hall.objects.create_hall(code=code, name=name)

    @classmethod
    def get_hall(cls, hall_id: int = None, code: str = None) -> Hall:
        return Hall.objects.get_hall(hall_id=hall_id, code=code)

    @classmethod
    def update_hall(cls, hall_id: int, **kwargs) -> Hall:
        hall = Hall.objects.get_hall(hall_id=hall_id)
        return hall.update_hall(**kwargs) if hall else None

    @classmethod
    def delete_hall(cls, hall_id: int) -> bool:
        hall = Hall.objects.get_hall(hall_id=hall_id)
        return hall.delete_hall() if hall else False


class movie_operations:
    @classmethod
    def create_movie(cls, code: str, title: str, **kwargs) -> Movie:
        return Movie.objects.create_movie(code=code, title=title, **kwargs)

    @classmethod
    def get_movie(cls, movie_id: int = None, code: str = None) -> Movie:
        return Movie.objects.get_movie(movie_id=movie_id, code=code)

    @classmethod
    def get_movies_by_genre(cls, genre: str) -> list:
        return Movie.objects.get_movies_by_genre(genre)

    @classmethod
    def update_movie(cls, movie_id: int, **kwargs) -> Movie:
        movie = Movie.objects.get_movie(movie_id=movie_id)
        return movie.update_movie(**kwargs) if movie else None

    @classmethod
    def delete_movie(cls, movie_id: int) -> bool:
        movie = Movie.objects.get_movie(movie_id=movie_id)
        return movie.delete_movie() if movie else False


class cinema_operations:
    @classmethod
    def create_cinema(cls, code: str, city: str, address: str) -> Cinema:
        return Cinema.objects.create_cinema(code=code, city=city, address=address)

    @classmethod
    def get_cinema(cls, cinema_id: int = None, code: str = None) -> Cinema:
        return Cinema.objects.get_cinema(cinema_id=cinema_id, code=code)

    @classmethod
    def get_cinemas_by_city(cls, city: str) -> list:
        return Cinema.objects.get_cinemas_by_city(city)

    @classmethod
    def update_cinema(cls, cinema_id: int, **kwargs) -> Cinema:
        cinema = Cinema.objects.get_cinema(cinema_id=cinema_id)
        return cinema.update_cinema(**kwargs) if cinema else None

    @classmethod
    def delete_cinema(cls, cinema_id: int) -> bool:
        cinema = Cinema.objects.get_cinema(cinema_id=cinema_id)
        return cinema.delete_cinema() if cinema else False


class showtime_operations:
    @classmethod
    def create_showtime(
            cls,
            code: str,
            movie_id: int,
            hall_id: int,
            cinema_id: int,
            start_time: datetime
    ) -> Showtime:
        return Showtime.objects.create_showtime(
            code=code,
            movie_id=movie_id,
            hall_id=hall_id,
            cinema_id=cinema_id,
            start_time=start_time
        )

    @classmethod
    def get_showtime(cls, showtime_id: int = None, code: str = None) -> Showtime:
        return Showtime.objects.get_showtime(showtime_id=showtime_id, code=code)

    @classmethod
    def get_available_seats(cls, showtime_id: int) -> list:
        showtime = Showtime.objects.get_showtime(showtime_id=showtime_id)
        return showtime.get_available_seats() if showtime else []

    @classmethod
    def init_seats(cls, showtime_id: int, seats: list):
        showtime = Showtime.objects.get_showtime(showtime_id=showtime_id)
        if showtime:
            showtime.init_seats(seats)

    @classmethod
    def get_showtimes_by_date(cls, date: datetime.date) -> list:
        return Showtime.objects.get_showtimes_by_date(date)

    @classmethod
    def get_showtimes_by_cinema(cls, cinema_id: int) -> list:
        return Showtime.objects.get_showtimes_by_cinema(cinema_id)

    @classmethod
    def update_showtime(cls, showtime_id: int, **kwargs) -> Showtime:
        showtime = Showtime.objects.get_showtime(showtime_id=showtime_id)
        return showtime.update_showtime(**kwargs) if showtime else None

    @classmethod
    def delete_showtime(cls, showtime_id: int) -> bool:
        showtime = Showtime.objects.get_showtime(showtime_id=showtime_id)
        return showtime.delete_showtime() if showtime else False


class ticket_operations:
    @classmethod
    def create_ticket(
            cls,
            showtime_id: int,
            user_id: int,
            price: float,
            seat: str
    ) -> Ticket:
        return Ticket.objects.create_ticket(
            showtime_id=showtime_id,
            user_id=user_id,
            price=price,
            seat=seat
        )

    @classmethod
    def get_ticket(cls, ticket_id: int = None, code: str = None) -> Ticket:
        return Ticket.objects.get_ticket(ticket_id=ticket_id, code=code)

    @classmethod
    def get_tickets_by_user(cls, user_id: int) -> list:
        return Ticket.objects.get_tickets_by_user(user_id)

    @classmethod
    def get_tickets_by_showtime(cls, showtime_id: int) -> list:
        return Ticket.objects.get_tickets_by_showtime(showtime_id)

    @classmethod
    def update_ticket(cls, ticket_id: int, **kwargs) -> Ticket:
        ticket = Ticket.objects.get_ticket(ticket_id=ticket_id)
        return ticket.update_ticket(**kwargs) if ticket else None

    @classmethod
    def delete_ticket(cls, ticket_id: int) -> bool:
        ticket = Ticket.objects.get_ticket(ticket_id=ticket_id)
        return ticket.delete_ticket() if ticket else False