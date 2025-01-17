import datetime
import time

from django.conf import settings
import django.db.models as models
from django.utils import timezone
from django.utils.dateparse import parse_datetime


class UnixDateTimeField(models.DateTimeField):

    # TODO(niklas9):
    # * should we take care of transforming between time zones in any way here ?
    # * get default datetime format from settings ?
    DEFAULT_DATETIME_FMT = '%Y-%m-%d %H:%M:%S'
    # TODO(niklas9):
    # * metaclass below just for Django < 1.9, fix a if stmt for it?
    #__metaclass__ = models.SubfieldBase
    description = "Unix timestamp integer to datetime object"

    def get_internal_type(self):
        return 'PositiveIntegerField'

    def to_python(self, val):
        if val is None or isinstance(val, datetime.datetime):
            return val
        if isinstance(val, datetime.date):
            return datetime.datetime(val.year, val.month, val.day)
        elif self._is_string(val):
            return parse_datetime(val)
        else:
            datetime_value = datetime.datetime.fromtimestamp(float(val))
            if settings.USE_TZ:
                # Unix timestamp is always UTC by definition
                try:
                    import pytz
                    return timezone.make_aware(datetime_value, timezone=pytz.timezone("UTC"))
                except ImportError:
                    return timezone.make_aware(datetime_value)
            else: 
                return datetime_value

    def _is_string(value, val):
        try:
            return isinstance(val, unicode)
        except NameError:
            return isinstance(val, str)

    def get_db_prep_value(self, val, *args, **kwargs):
        if val is None:
            if self.default == models.fields.NOT_PROVIDED:  return None
            return self.default
        return int(time.mktime(val.timetuple()))

    def value_to_string(self, obj):
        val = self._get_val_from_obj(obj)
        return self.to_python(val).strftime(self.DEFAULT_DATETIME_FMT)

    def from_db_value(self, val, *args, **kwargs):
        return self.to_python(val)
