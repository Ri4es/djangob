from django import forms
from .models import Showtime


class BookingForm(forms.Form):
    seat = forms.ChoiceField(
        label='Выберите место',
        choices=[],
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        showtime_id = kwargs.pop('showtime_id', None)
        super().__init__(*args, **kwargs)

        if showtime_id:
            from .services import ShowtimeService
            available_seats = ShowtimeService.get_available_seats(showtime_id)
            self.fields['seat'].choices = [(seat, seat) for seat in available_seats]