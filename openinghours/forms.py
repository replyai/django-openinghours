"""Editing form for opening hours

Front-end untrusted end user grade UX aimed at business directory sites.

UX supports up to 2 sets of opening hours per day optimised for common stories:
9 till 5, closed for lunch, open till late, Saturday morning-closed on Sunday
"""
import pytz
from django import forms
from datetime import time, datetime
from .app_settings import TIME_FORMAT
from .models import ClosingRules
from .utils import apply_timezone, as_timezone


def str_to_time(s):
    """ Turns strings like '08:30' to time objects """
    str_format = '%H:%M'
    if TIME_FORMAT == 12:
        str_format = '%I:%M %p'
    return datetime.strptime(s, str_format).time()


def time_to_str(t):
    """ Turns time objects to strings like '08:30' """
    time_format = '%H:%M'
    if TIME_FORMAT == 12:
        time_format = '%I:%M %p'
    return t.strftime(time_format)


def time_choices():
    """Return digital time choices every half hour from 00:00 to 23:30."""
    hours = list(range(0, 24))
    times = []
    for h in hours:
        hour = str(h).zfill(2)
        cur_time = hour+':00'
        if TIME_FORMAT != 24:
            cur_time = datetime.strptime(cur_time, "%H:%M")
            cur_time = cur_time.strftime("%I:%M %p")
        times.append(cur_time)
        cur_time = hour + ':30'
        if TIME_FORMAT != 24:
            cur_time = datetime.strptime(cur_time, "%H:%M")
            cur_time = cur_time.strftime("%I:%M %p")
        times.append(cur_time)
    return list(zip(times, times))

TIME_CHOICES = time_choices()


class Slot(forms.Form):
    opens = forms.ChoiceField(choices=TIME_CHOICES)
    shuts = forms.ChoiceField(choices=TIME_CHOICES)


class ClosingRulesForm(forms.ModelForm):
    start_time = forms.ChoiceField(choices=TIME_CHOICES)
    end_time = forms.ChoiceField(choices=TIME_CHOICES)
    start_date = forms.DateField(label='Start date')
    end_date = forms.DateField(label='End date')

    def clean_start_time(self):
        return str_to_time(self.cleaned_data.get('start_time'))

    def clean_end_time(self):
        return str_to_time(self.cleaned_data.get('end_time'))

    def clean_reason(self):
        return self.cleaned_data.get('reason', '')

    def __init__(self, *args, **kwargs):
        super(ClosingRulesForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            timezone_name = self.instance.company.timezone
            start = as_timezone(self.instance.start, timezone_name)
            end = as_timezone(self.instance.end, timezone_name)

            self.fields['start_date'].initial = start.date()
            self.fields['end_date'].initial = end.date()
            self.fields['start_time'].initial = time_to_str(start.time())
            self.fields['end_time'].initial = time_to_str(end.time())

    class Meta:
        model = ClosingRules
        fields = ('reason', )
        widgets = {
            'reason': forms.TextInput(),
        }

