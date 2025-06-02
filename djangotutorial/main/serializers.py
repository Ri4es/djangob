from rest_framework import serializers
from .models import Ticket, Showtime


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ['id', 'code', 'showtime', 'price', 'seat']
        extra_kwargs = {
            'code': {'read_only': True},
            'showtime': {'required': True},
            'seat': {'required': True}
        }