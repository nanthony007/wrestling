# module for scoring event classes


import attr
from attr.validators import in_, instance_of

from datetime import time

import abc

from wrestling import base


# todo: find a way to validate period based on timestamp.


@attr.s(slots=True, eq=True, order=True, auto_attribs=True, kw_only=True)
class ScoringEvent(object):
    time_stamp: time = attr.ib(validator=instance_of(time), order=True)
    initiator: str = attr.ib(
        validator=[instance_of(str), in_(("red", "green"))], order=False,
    )
    focus_color: str = attr.ib(
        validator=[instance_of(str), in_(("red", "green"))], order=False, repr=False
    )
    period: int = attr.ib(validator=instance_of(int), order=False,
                          repr=False)

    @property
    @abc.abstractmethod
    def label(self):
        pass

    @time_stamp.validator
    def check_time_stamp(self, attribute, val):
        if val.hour != 0:
            raise ValueError(f"`hour` field of timestamp must be 0 (zero).")

    @property
    def formatted_time(self):
        return time.strftime(self.time_stamp, "%M:%S")

    @property
    def formatted_label(self):
        if self.focus_color == self.initiator:
            return f"f{self.label.tag}"
        elif self.focus_color != self.initiator:
            return f"o{self.label.tag}"
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


@attr.s(slots=True, eq=True, order=True, auto_attribs=True, kw_only=True)
class CollegeScoring(ScoringEvent):
    label: base.CollegeLabel = attr.ib(validator=instance_of(base.CollegeLabel),
                                       order=False, repr=lambda x: x.tag)


@attr.s(slots=True, eq=True, order=True, auto_attribs=True, kw_only=True)
class HSScoring(ScoringEvent):
    label: base.HSLabel = attr.ib(validator=instance_of(base.HSLabel), order=False,
                                  repr=lambda x: x.tag)
