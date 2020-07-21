# module for wrestler classes

from typing import Optional, Dict, Tuple
import attr
from attr.validators import instance_of
from wrestling.enumerations import Year


def _convert_to_title(x: str):
    return x.title().strip()


@attr.s(kw_only=True, auto_attribs=True, order=True)
class Wrestler(object):
    name: str = attr.ib(
        converter=_convert_to_title, validator=instance_of(str), order=True
    )
    team: str = attr.ib(
        converter=_convert_to_title, validator=instance_of(str), order=False
    )
    year: Optional[Year] = attr.ib(
        validator=[instance_of(Year)], default=Year.FR, order=False
    )

    @name.validator
    def _check_name(self, attrib, val):
        if ", " not in val:
            raise ValueError(f"Names should be formatted as `Last, First`, got {val}.")

    def to_dict(self):
        return dict(
            name=self.name,
            team=self.team,
            year=self.year.value
        )
