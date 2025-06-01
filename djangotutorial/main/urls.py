from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from .api import TicketViewSet

router = DefaultRouter()
router.register(r'tickets', TicketViewSet, basename='ticket')

urlpatterns = [
    path('', views.index ),
    path('about-us', views.about),
    path('movies/', views.movie_list, name='movie_list'),
    path('movies/<int:movie_id>/', views.movie_detail, name='movie_detail'),
    path('showtimes/', views.showtime_list, name='showtime_list'),
    path('showtimes/<int:showtime_id>/', views.showtime_detail, name='showtime_detail'),
    path('book-ticket/<int:showtime_id>/', views.book_ticket, name='book_ticket'),
    path('my-tickets/', views.my_tickets, name='my_tickets'),
    path('ticket/<int:ticket_id>/', views.ticket_detail, name='ticket_detail'),
path('api/', include(router.urls)),
]
