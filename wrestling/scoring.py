# module for scoring event classes


import attr
from attr.validators import in_, instance_of

from datetime import time

import abc

from wrestling.enumerations import CollegeLabel, HighSchoolLabel


# todo: add subclass for custom actions (which takes custom Labels Enum)


@attr.s(frozen=True, slots=True, eq=True, order=True, auto_attribs=True, kw_only=True)
class _ScoringEvent(object):
    time_stamp: time = attr.ib(validator=instance_of(time), order=True)
    initiator: str = attr.ib(
        validator=[instance_of(str), in_(("red", "green"))], order=False,
    )
    focus_color: str = attr.ib(
        validator=[instance_of(str), in_(("red", "green"))], order=False, repr=False
    )
    period: int = attr.ib(validator=instance_of(int), order=False, repr=False)

    @period.validator
    def _check_period(self, attrib, val):
        if val >= 5 or val < 1:
            raise ValueError(f"Expected period between 1-4, got {val!r}.")

    @time_stamp.validator
    def _check_time_stamp(self, _, val):
        if val.hour != 0:
            raise ValueError(f"`hour` field of timestamp must be 0 (zero).")

    @property
    def formatted_time(self):
        return time.strftime(self.time_stamp, "%M:%S")

    @property
    def formatted_label(self):
        if self.label.name == 'START':
            return 'START'
        if self.focus_color == self.initiator:
            return f"f{self.label.name}"
        elif self.focus_color != self.initiator:
            return f"o{self.label.name}"
        else:
            raise ValueError(
                f'Expected "red" or "green" '
                f"for `focus_color` AND "
                f"`initiator`, got {self.focus_color} and "
                f"{self.initiator}."
            )

    def to_dict(self):
        return dict(
            time=self.formatted_time,
            period=self.period,
            str_label=self.formatted_label,
            label=self.label
        )


@attr.s(frozen=True, slots=True, eq=True, order=True, auto_attribs=True, kw_only=True)
class CollegeScoring(_ScoringEvent):
    label: CollegeLabel = attr.ib(validator=instance_of(CollegeLabel), order=False)


@attr.s(frozen=True, slots=True, eq=True, order=True, auto_attribs=True, kw_only=True)
class HighSchoolScoring(_ScoringEvent):
    label: HighSchoolLabel = attr.ib(
        validator=instance_of(HighSchoolLabel), order=False
    )
