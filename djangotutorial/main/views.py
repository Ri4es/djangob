from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Movie, Showtime, Ticket, Cinema
from .services import ShowtimeService, TicketService
from .forms import BookingForm


def index(request):
    # Показываем последние фильмы и сеансы
    movies = Movie.objects.order_by('-release_date')[:5]
    now = timezone.now()
    upcoming_showtimes = Showtime.objects.filter(
        start_time__gte=now
    ).order_by('start_time')[:10]

    return render(request, 'main/index.html', {
        'movies': movies,
        'showtimes': upcoming_showtimes
    })


def about(request):
    return render(request, 'main/about.html')


def movie_list(request):
    movies = Movie.objects.all().order_by('-release_date')
    return render(request, 'main/movie_list.html', {'movies': movies})


def movie_detail(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    showtimes = Showtime.objects.filter(
        movie=movie,
        start_time__gte=timezone.now()
    ).order_by('start_time')

    return render(request, 'main/movie_detail.html', {
        'movie': movie,
        'showtimes': showtimes
    })


def showtime_list(request):
    now = timezone.now()
    showtimes = Showtime.objects.filter(
        start_time__gte=now
    ).order_by('start_time').select_related('movie', 'cinema', 'hall')

    # Группировка по дате
    showtimes_by_date = {}
    for showtime in showtimes:
        date = showtime.start_time.date()
        if date not in showtimes_by_date:
            showtimes_by_date[date] = []
        showtimes_by_date[date].append(showtime)

    return render(request, 'main/showtime_list.html', {
        'showtimes_by_date': showtimes_by_date
    })


def showtime_detail(request, showtime_id):
    showtime = get_object_or_404(
        Showtime.objects.select_related('movie', 'cinema', 'hall'),
        id=showtime_id
    )

    # Инициализация мест при первом открытии
    if not showtime.available_seats:
        seats = [f"{row}{num}" for row in "ABCDEFGH" for num in range(1, 21)]
        ShowtimeService.init_seats(showtime.id, seats)

    form = BookingForm(showtime_id=showtime_id)

    return render(request, 'main/showtime_detail.html', {
        'showtime': showtime,
        'form': form
    })


@login_required
def book_ticket(request, showtime_id):
    showtime = get_object_or_404(Showtime, id=showtime_id)

    if request.method == 'POST':
        form = BookingForm(request.POST, showtime_id=showtime_id)
        if form.is_valid():
            seat = form.cleaned_data['seat']

            try:
                # Бронируем билет
                ticket = TicketService.book_ticket(
                    showtime_id=showtime.id,
                    user_id=request.user.id,
                    seat=seat
                )
                return redirect('ticket_detail', ticket_id=ticket.id)

            except Exception as e:
                return render(request, 'main/showtime_detail.html', {
                    'showtime': showtime,
                    'form': form,
                    'error': str(e)
                })

    return redirect('showtime_detail', showtime_id=showtime_id)


@login_required
def my_tickets(request):
    # Показываем билеты текущего пользователя
    tickets = Ticket.objects.filter(user=request.user).select_related(
        'showtime__movie', 'showtime__cinema', 'showtime__hall'
    ).order_by('-booking_date')

    return render(request, 'main/my_tickets.html', {'tickets': tickets})


@login_required
def ticket_detail(request, ticket_id):
    ticket = get_object_or_404(
        Ticket.objects.select_related(
            'showtime__movie',
            'showtime__cinema',
            'showtime__hall'
        ),
        id=ticket_id,
        user=request.user
    )
    return render(request, 'main/ticket_detail.html', {'ticket': ticket})