# module for events classes

import attr
from attr.validators import in_, instance_of

from datetime import date
import warnings


def convert_event_name(x: str):
    """Acts as converter."""
    if len(x) == 0:
        warnings.warn(f'String cannot be empty, set to "Generic Event".', UserWarning)
        return "Generic Event"
    return x.title().strip()


@attr.s(kw_only=True, auto_attribs=True, order=False, slots=True, frozen=True)
class Event(object):
    id_: str = attr.ib(validator=instance_of(str), repr=False)
    name: str = attr.ib(converter=convert_event_name, validator=instance_of(str))
    type_: str = attr.ib(
        validator=[instance_of(str), in_(("Tournament", "Dual Meet"))]
    )

    @id_.validator
    def _check_event_id(self, _, val):
        if len(val) < 20 or len(val) > 50:
            raise ValueError(
                f"Expected str `id_` with 20 <= len <= 50, " f'got "{val}"'
            )

    def to_dict(self):
        return dict(
            name=self.name,
            type=self.type_,
        )
