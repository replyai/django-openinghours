"""Editing form for opening hours

Front-end untrusted end user grade UX aimed at business directory sites.

UX supports up to 2 sets of opening hours per day optimised for common stories:
9 till 5, closed for lunch, open till late, Saturday morning-closed on Sunday
"""

from django import forms
from datetime import time, datetime
from .app_settings import TIME_FORMAT


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
