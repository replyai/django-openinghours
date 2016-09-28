from django.conf import settings
DEFAULT_MODEL = 'openinghours.Company'
PREMISES_MODEL = getattr(settings, 'OPENINGHOURS_PREMISES_MODEL', DEFAULT_MODEL)

TIME_FORMAT = getattr(settings, 'OPENINGHOURS_TIME_FORMAT', 12)
