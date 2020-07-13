# module for wrestler classes

from typing import Optional
import attr
from attr.validators import instance_of

from wrestling.enumerations import Year


# todo: add method for calculating all the athlete metrics!
#  (should be in college / hs --> reason for subclasses) --> NO BECAUSE THOSE
#  MATCHES/SCORING EVENTS ALREADY CONTAIN EXCLUSIVELY THE CORRECT EVENT LABELS -->
#  THIS IS AWESOME AND MEANS ONE DYNAMIC WRESTLER CLASS CAN ACCOMPLISH EVERYTHING!


def convert_to_title(x: str):
    return x.title().strip()


@attr.s(kw_only=True, auto_attribs=True, order=True, slots=True, frozen=True)
class Wrestler(object):
    name: str = attr.ib(converter=convert_to_title, validator=instance_of(str),
                        order=True)
    team: str = attr.ib(converter=convert_to_title, validator=instance_of(str),
                        order=False)
    eligibility: Optional[Year] = attr.ib(
        validator=[instance_of(Year)],
        default=Year.FR, order=False
    )

    @name.validator
    def _check_name(self, attrib, val):
        assert ", " in val, f"Names should be formatted as `Last, First`, got {val}."
