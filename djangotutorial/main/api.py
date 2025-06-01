from rest_framework import viewsets, status
from rest_framework.response import Response
from .services import TicketService
from .serializers import TicketSerializer
from .models import Ticket
from django.core.exceptions import ValidationError
from django.db import IntegrityError

class TicketViewSet(viewsets.ModelViewSet):

    queryset = Ticket.objects.none()
    serializer_class = TicketSerializer
