# module for events classes

import attr
from attr.validators import instance_of
import logging
from wrestling import base
import warnings

logging.basicConfig(filename='logfile.log', filemode='a')
logger = logging.getLogger('Event')


def convert_event_name(x: str):
    """Acts as converter."""
    if len(x) == 0:
        message = f'String cannot be empty, set to "Generic Event".'
        warnings.warn(message, UserWarning)
        return "Generic Event"
    return x.title().strip()


@attr.s(auto_attribs=True, order=False, eq=True, slots=True)
class Event(object):
    id: str = attr.ib(validator=instance_of(str), repr=False)
    name: str = attr.ib(converter=convert_event_name, validator=instance_of(str))
    _type: base.Mark = attr.ib(
        validator=instance_of(base.Mark), repr=lambda x: x.tag, eq=False
    )

    def __attrs_post_init__(self):
        self.check_type_input()

    @property
    def type(self):
        return self._type.tag

    def check_type_input(self):
        if self._type.tag not in {"Tournament", "Dual Meet"}:
            message = f'Invalid Event type, expected one of "Tournament", ' \
                      f'"Dual Meet", got {self._type.tag!r}.'
            self._type.isvalid = False
            self._type.msg = message
            logger.info(message)

    def to_dict(self):
        return dict(
            name=self.name,
            type=self.type,
        )
