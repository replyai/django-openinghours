from django.conf import settings

PREMISES_MODEL = getattr(settings, 'OPENINGHOURS_PREMISES_MODEL',
                                   'openinghours.Company')

TIME_FORMAT = getattr(settings, 'OPENINGHOURS_TIME_FORMAT', 12)
