from datetime import timedelta, tzinfo

# The following tzinfo code comes from the Python standard
# library documentation
ZERO = timedelta(0)


# A UTC class.
class UTC(tzinfo):
    """UTC"""
    def __repr__(self):
        return 'UTC'

    def utcoffset(self, dt):
        return ZERO

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return ZERO


utc = UTC()
