# module for events classes

import attr
from attr.validators import instance_of
from wrestling import base
import warnings


def convert_event_name(x: str):
    """Acts as converter."""
    if len(x) == 0:
        message = f'String cannot be empty, set to "Generic Event".'
        warnings.warn(message, UserWarning)
        logger.info(message)
        return "Generic Event"
    return x.title().strip()


@attr.s(auto_attribs=True, order=False, eq=True, slots=True)
class Event(object):
    name: str = attr.ib(converter=convert_event_name, validator=instance_of(str))
    _kind: base.Mark = attr.ib(
        validator=instance_of(base.Mark), repr=lambda x: x.tag, eq=False,
    )

    def __attrs_post_init__(self):
        self.type_input_handler()

    @property
    def kind(self):
        return self._kind.tag

    def type_input_handler(self):
        if self._kind.tag not in {"Tournament", "Dual Meet"}:
            message = f'Invalid Event type, expected one of "Tournament", ' \
                      f'"Dual Meet", got {self._kind.tag!r}.'
            self._kind.isvalid = False
            self._kind.msg = message
            logger.info(message)

    def to_dict(self):
        return dict(
            name=self.name,
            kind=self.kind,
        )
