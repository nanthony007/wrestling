# module for scoring event classes


import attr
from attr.validators import in_, instance_of

from datetime import time

import abc

from wrestling.enumerations import CollegeLabel, HighSchoolLabel


# todo: add subclass for custom actions (which takes custom Labels Enum)


@attr.s(frozen=True, slots=True, eq=True, order=True, auto_attribs=True, kw_only=True)
class ScoringEvent(object):
    time_stamp: time = attr.ib(validator=instance_of(time), order=True)
    initiator: str = attr.ib(
        validator=[instance_of(str), in_(("red", "green"))], order=False,
    )
    focus_color: str = attr.ib(
        validator=[instance_of(str), in_(("red", "green"))], order=False, repr=False
    )

    @time_stamp.validator
    def _check_time_stamp(self, _, val):
        if val.hour != 0:
            raise ValueError(f"`hour` field of timestamp must be 0 (zero).")

    @property
    def formatted_time(self):
        return time.strftime(self.time_stamp, "%M:%S")

    @abc.abstractmethod
    def todict(self):
        pass


@attr.s(frozen=True, slots=True, eq=True, order=True, auto_attribs=True, kw_only=True)
class CollegeScoring(ScoringEvent):
    label: CollegeLabel = attr.ib(validator=instance_of(CollegeLabel), order=False)

    @property
    def period(self):
        if 0 <= self.time_stamp.minute < 3:
            return 1
        elif 3 <= self.time_stamp.minute < 5:
            return 2
        elif 5 <= self.time_stamp.minute < 7:
            return 3
        elif self.time_stamp.minute >= 7:
            return 4
        else:
            raise ValueError(
                f"Unexpected time value: {self.time_stamp}, "
                f"could not determine `period`."
            )

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

    def todict(self):
        return dict(
            time=self.formatted_time,
            period=self.period,
            label=self.formatted_label,
        )


@attr.s(frozen=True, slots=True, eq=True, order=True, auto_attribs=True, kw_only=True)
class HighSchoolScoring(ScoringEvent):
    label: HighSchoolLabel = attr.ib(
        validator=instance_of(HighSchoolLabel), order=False
    )

    @property
    def period(self):
        if 0 <= self.time_stamp.minute < 2:
            return 1
        elif 2 <= self.time_stamp.minute < 4:
            return 2
        elif 4 <= self.time_stamp.minute < 6:
            return 3
        elif self.time_stamp.minute >= 6:
            return 4
        else:
            raise ValueError(
                f"Unexpected time value: {self.time_stamp}, "
                f"could not determine `period`."
            )

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

    def todict(self):
        return dict(
            time=self.formatted_time,
            period=self.period,
            label=self.formatted_label,
        )
