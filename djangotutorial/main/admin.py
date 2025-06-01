from django.contrib import admin

# Register your models here.
from .models import Hall, Movie, Showtime, Ticket


@admin.register(Hall)
class HallAdmin(admin.ModelAdmin):
    list_display  = ('code', 'name')
    search_fields = ('code', 'name')


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display  = ('code', 'title', 'genre', 'rating', 'release_date')
    search_fields = ('code', 'title', 'genre')


@admin.register(Showtime)
class ShowtimeAdmin(admin.ModelAdmin):
    list_display  = ('code', 'movie', 'hall', 'start_time')
    list_filter   = ('hall', 'movie')
    search_fields = ('code',)


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display  = ('code', 'showtime', 'user', 'seat', 'price')
    list_filter   = ('showtime__hall', 'showtime__movie')
    search_fields = ('code', 'seat', 'user__username')