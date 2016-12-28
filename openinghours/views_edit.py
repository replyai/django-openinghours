import pytz
from collections import OrderedDict

from datetime import datetime
from django.http import HttpResponseRedirect
from django.utils.encoding import force_text
from django.views.generic import DetailView, UpdateView

from openinghours.forms import Slot, time_to_str, str_to_time
from openinghours.models import OpeningHours, WEEKDAYS, ClosingRules
from openinghours.utils import get_premises_model
from .forms import ClosingRulesForm
from .utils import construct_tz_aware_time
from django.forms import modelformset_factory


class OpeningHoursEditView(DetailView, UpdateView):
    """
    Powers editing UI supporting up to 2 time slots (sets) per day.

    Models still support more slots via shell or admin UI.
    This UI will delete and not recreate anything above 2 daily slots.

    Inspired by Google local opening hours UI and earlier works.
    """
    model = get_premises_model()
    template_name = "openinghours/edit_base.html"
    include_form_actions = True

    def form_prefix(self, day_n, slot_n):
        """Form prefix made up of day number and slot number.

        - day number 1-7 for Monday to Sunday
        - slot 1-2 typically morning and afternoon
        """
        return "day%s_%s" % (day_n, slot_n)

    def get_success_url(self):
        """
        Returns the supplied success URL.
        """
        if not self.success_url:
            self.success_url = self.request.path_info
        if self.success_url:
            # Forcing possible reverse_lazy evaluation
            url = force_text(self.success_url)
        else:
            url = self.request.path_info
        return url

    def get_context_data(self, **kwargs):
        """
        Initialize the editing form

        1. Build opening_hours, a lookup dictionary to populate the form
           slots: keys are day numbers, values are lists of opening
           hours for that day.
        2. Build days, a list of days with 2 slot forms each.
        3. Build form initials for the 2 slots padding/trimming
           opening_hours to end up with exactly 2 slots even if it's
           just None values.
        """
        self.object = self.get_object()
        context = super(OpeningHoursEditView, self).get_context_data(**kwargs)
        two_sets = False
        closed = None
        opening_hours = {}
        for o in OpeningHours.objects.filter(company=self.object):
            opening_hours.setdefault(o.weekday, []).append(o)
        days = []
        for day_no, day_name in WEEKDAYS:
            if day_no not in opening_hours.keys():
                closed = True
                ini1, ini2 = [None, None]
            else:
                closed = False
                ini = [{'opens': time_to_str(oh.from_hour),
                        'shuts': time_to_str(oh.to_hour)}
                       for oh in opening_hours[day_no]]
                ini += [None] * (2 - len(ini[:2]))  # pad
                ini1, ini2 = ini[:2]  # trim
                if ini2:
                    two_sets = True
            days.append({
                'name': day_name,
                'number': day_no,
                'slot1': Slot(prefix=self.form_prefix(day_no, 1), initial=ini1),
                'slot2': Slot(prefix=self.form_prefix(day_no, 2), initial=ini2),
                'closed': closed
            })
        context['days'] = days
        context['two_sets'] = two_sets
        context['location'] = self.object
        context['include_form_actions'] = self.include_form_actions
        closing_rules_queryset = ClosingRules.objects.filter(company=self.object.pk)
        extra = 2
        if closing_rules_queryset.count() == 0:
            extra = 3
        formset = modelformset_factory(ClosingRules, ClosingRulesForm, extra=extra)
        context['formset'] = formset(queryset=closing_rules_queryset)
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def process_post(self, request):
        """
        Clean the data and save opening hours in the database.
        Old opening hours are purged before new ones are saved.
        """
        location = self.get_object()
        # open days, disabled widget data won't make it into request.POST
        present_prefixes = [x.split('-')[0] for x in request.POST.keys()]

        day_forms = OrderedDict()
        for day_no, day_name in WEEKDAYS:
            for slot_no in (1, 2):
                prefix = self.form_prefix(day_no, slot_no)
                # skip closed day as it would be invalid form due to no data
                if prefix not in present_prefixes:
                    continue
                day_forms[prefix] = (day_no, Slot(request.POST, prefix=prefix))

        if all([day_form[1].is_valid() for pre, day_form in day_forms.items()]):
            OpeningHours.objects.filter(company=location).delete()
            for prefix, day_form in day_forms.items():
                day, form = day_form
                opens, shuts = [str_to_time(form.cleaned_data[x])
                                for x in ('opens', 'shuts')]
                if opens != shuts:
                    OpeningHours(from_hour=opens, to_hour=shuts,
                                 company=location, weekday=day).save()

        # assume that forms are validated
        ClosingRulesFormSet = modelformset_factory(ClosingRules, ClosingRulesForm)
        formset = ClosingRulesFormSet(request.POST)
        for form in formset.forms:
            if form.is_valid():
                closing_rule = form.save(commit=False)
                closing_rule.start = construct_tz_aware_time(form.cleaned_data['start_date'],
                                                                  form.cleaned_data['start_time'],
                                                                  location.timezone)
                closing_rule.end = construct_tz_aware_time(form.cleaned_data['end_date'],
                                                                  form.cleaned_data['end_time'],
                                                                  location.timezone)
                closing_rule.company = location
                closing_rule.save()
            elif form.is_bound:
                ClosingRules.objects.filter(pk=form.instance.pk).delete()

    def post(self, request, *args, **kwargs):
        self.process_post(request)
        success_url = self.get_success_url()
        return HttpResponseRedirect(success_url)


