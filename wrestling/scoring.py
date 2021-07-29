#! /usr/bin/python

"""Module for Scoring Events.

This module builds the Scoring Events base class with validation
for its fields. When validation is stronger than simple type
validation, the Mark class is used in replace of traditional
str or int classes to track accuracy.

Example:
    >>>scoring_event = CollegeScoring(
        time_stamp=time(hour=0, minute=5, second=15),
        initiator='red',
        focus_color='green',
        period=2,
        label=CollegeLabel('T2')
    )

Todo:
    * Find a way to validate period based on timestamp.

"""

import abc
from datetime import time
from typing import Dict, Union

import attr
from attr.validators import in_, instance_of

from wrestling import base
from wrestling.base import CollegeLabel, HSLabel


@attr.s(slots=True, eq=True, order=True, auto_attribs=True, kw_only=True)
class ScoringEvent(object):
    """Scoring Event base class for any scoring action in a match.

    Args:
        time_stamp (time): Time the action occured.
        initiator (str): Who initiated the action, red or green.
        focus_color (str): Focus of the match.
        period (int): Period in which the action occured.

    Raises:
        ValueError: Hour parameter of time_stamp cannot be non-zero.
        ValueError: 'focus_color' and 'initiator' must be either 'red' or 'green'

    """

    time_stamp: Union[time, str] = attr.ib(validator=instance_of((time, str)), order=True)
    # TODO can probably remove these two fields
    initiator: str = attr.ib(
        validator=[instance_of(str), in_(("red", "green"))], order=False,
    )
    focus_color: str = attr.ib(
        validator=[instance_of(str), in_(("red", "green"))], order=False, repr=False
    )
    period: int = attr.ib(validator=instance_of(int), order=False, repr=False)
    focus_score: int = attr.ib(default=0, init=False, order=False, eq=False)
    opp_score: int = attr.ib(default=0, init=False, order=False, eq=False)

    @property
    @abc.abstractmethod
    def label(self):
        """Label of the action that occurred."""
        pass

    @time_stamp.validator
    def check_time_stamp(self, attribute, val):
        """Attrs validator, checks timestamp that hour is not zero."""
        if str(val).split(':')[0] != '00':
                raise ValueError(f"`hour` field of timestamp must be 0 (zero).")

    @property
    def formatted_time(self) -> str:
        """String formatted time.

        Returns:
            str: Minute:Second string formatted time_stamp.

        """
        return str(self.time_stamp)[3:]

    # TODO: this will then need adjusting/removal
    @property
    def formatted_label(self) -> str:
        """String formatted label.

        Raises:
            ValueError: initiator and focus_color must be either red or green.

        Returns:
            str: Label with focus (f) or opponent (o) prefix.

        """
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

    def to_dict(self) -> Dict[str, Union[int, str, CollegeLabel, HSLabel]]:
        """Converts instance to dict.

        Returns:
            Dict: Dictionary representation of Scoring Event instance.
        """
        return dict(
            time=self.formatted_time,
            period=self.period,
            str_label=self.formatted_label,
            label=self.label,
            focus_score=self.focus_score,
            opp_score=self.opp_score,
        )


@attr.s(slots=True, eq=True, order=True, auto_attribs=True, kw_only=True)
class CollegeScoring(ScoringEvent):
    """College version of a Scoring Event.

    Args:
        label (CollegeLabel): Label for the action.

    """

    label: base.CollegeLabel = attr.ib(
        validator=instance_of(base.CollegeLabel), order=False, repr=lambda x: x.tag
    )


@attr.s(slots=True, eq=True, order=True, auto_attribs=True, kw_only=True)
class HSScoring(ScoringEvent):
    """High School version of a Scoring Event.

    Args:
        label (HSLabel): Label for the action.
    """

    label: base.HSLabel = attr.ib(
        validator=instance_of(base.HSLabel), order=False, repr=lambda x: x.tag
    )
