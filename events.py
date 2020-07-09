# module for events classes

import attr
from attr.validators import in_, instance_of

import warnings


def convert_event_name(x: str):
    """Acts as converter."""
    if len(x) == 0:
        warnings.warn(f'String cannot be empty, set to "Generic Event".',
                      UserWarning)
        return 'Generic Event'
    return x.title().strip()


@attr.s(kw_only=True, auto_attribs=True, order=False, slots=True, frozen=True)
class Event(object):
    event_id: str = attr.ib(validator=instance_of(str), repr=False)
    event_name: str = attr.ib(converter=convert_event_name, validator=instance_of(str))
    event_type: str = attr.ib(validator=[instance_of(str), in_(("Tournament",
                                                                "Dual Meet"))])

    @event_id.validator
    def _check_event_id(self, _, val):
        if len(val) < 20 or len(val) > 50:
            raise ValueError(f'Expected str `event_id` with 20 <= len <= 50, '
                             f'got "{val}"')
