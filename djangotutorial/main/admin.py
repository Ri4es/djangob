from django.contrib import admin

from .models import Hall, Movie, Showtime, Ticket, Cinema
from .services import ShowtimeService
from django.core.exceptions import ValidationError


@admin.register(Hall)
class HallAdmin(admin.ModelAdmin):
    list_display  = ('code', 'name')
    search_fields = ('code', 'name')


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display  = ('code', 'title', 'genre', 'rating', 'release_date')
    search_fields = ('code', 'title', 'genre')

@admin.register(Cinema)
class CinemaAdmin(admin.ModelAdmin):
    list_display = ('code', 'city', 'address')
    search_fields = ('code', 'city', 'address')


@admin.register(Showtime)
class ShowtimeAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        try:
            if change:  # Обновление существующего объекта
                updates = {}
                for field in ['code', 'movie', 'hall', 'cinema', 'start_time']:
                    if field in form.changed_data:
                        updates[field] = getattr(obj, field)

                ShowtimeService.update_showtime(obj.id, **updates)
            else:  # Создание нового объекта
                ShowtimeService.create_showtime(
                    code=obj.code,
                    movie_id=obj.movie.id,
                    hall_id=obj.hall.id,
                    cinema_id=obj.cinema.id,
                    start_time=obj.start_time
                )
        except ValidationError as e:
            from django.contrib import messages
            messages.error(request, str(e))


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display  = ('code', 'showtime', 'user', 'seat', 'price')
    list_filter   = ('showtime__hall', 'showtime__movie')
    search_fields = ('code', 'seat', 'user__username')