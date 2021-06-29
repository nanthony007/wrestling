#! /usr/bin/python

"""Module for Matches.

This module builds the Match base class with validation
for its fields. When validation is stronger than simple type
validation, the Mark class is used in replace of traditional str or int classes to
track accuracy.

Example:
    >>>match = CollegeMatch(**kwargs)

"""

from datetime import datetime, time
from collections import Counter
from typing import Optional, Dict, Tuple, Union
from urllib.parse import quote

import attr
from attr.validators import instance_of

from wrestling import base
from wrestling.events import Event
from wrestling.scoring import CollegeScoring, HSScoring
from wrestling.sequence import isvalid_sequence
from wrestling.wrestlers import Wrestler


@attr.s(slots=True, order=True, eq=True, kw_only=True, auto_attribs=True)
class Match(object):
    """Match base class.

    Args:
        id (str): Match id.
        base_url (Optional[Union[str, None]]): Url to prepend to 'id', default to None.
        event (Event): Event instance for the event the match occurred at.
        date (datetime): Datetime the match occurred at.
        result (Result): Result of the match.
        overtime ([Optional[bool]]): If the match went into overtime, default to False.
        focus (Wrestler): Wrestler instance for the primary wrestler.
        opponent (Wrestler): Wrestler instance for the opponent.
        weight (Mark): Weight class the match was contested at.
        isvalid (bool): Whether the match is valid or has errors.
        invalid_messages (tuple): Tuple of (brief) match error messages, can be empty.
        invalid_count (int): Count of invalid Marks found in the match.

    Raises:
        ValueError: Overtime cannot be True if Result method is Tech.

    """

    _id: str = attr.ib(validator=instance_of(str), repr=False, order=False)
    # enter at your own risk
    base_url: Optional[Union[str, None]] = attr.ib(
        default=None, repr=False, order=False
    )
    event: Event = attr.ib(
        validator=instance_of(Event), repr=lambda x: x.name, order=False
    )
    date: Union[str, datetime] = attr.ib(validator=instance_of((datetime, str)), order=True, repr=False)
    result: base.Result = attr.ib(
        validator=instance_of(base.Result), order=False, repr=lambda x: x.text
    )
    overtime: Optional[bool] = attr.ib(
        validator=instance_of(bool), order=False, repr=False, default=False
    )
    focus: Wrestler = attr.ib(
        validator=instance_of(Wrestler), order=False, repr=lambda x: x.name
    )
    opponent: Wrestler = attr.ib(
        validator=instance_of(Wrestler), order=False, repr=lambda x: x.name
    )
    _weight: base.Mark = attr.ib(validator=instance_of(base.Mark), repr=lambda x: x.tag)
    isvalid: bool = attr.ib(init=False, repr=False, order=False, eq=False)
    invalid_messages: Tuple = attr.ib(
        init=False, factory=tuple, repr=False, order=False, eq=False
    )
    invalid_count: int = attr.ib(init=False, repr=False, order=False, eq=False)

    def __attrs_post_init__(self):
        """Post init function to call Mark input handlers."""
        self.check_weight_input()
        self.isvalid = self.set_validity()

    @overtime.validator
    def check_overtime(self, attribute, value):
        """Checks overtime validity."""
        if self.result == base.Result.WT or self.result == base.Result.LT:
            if value:  # if overtime is True
                raise ValueError(f"Overtime must be false if match resulted in Tech.")

    @property
    def weight(self) -> str:
        """Weight class match contested at.

        Returns:
            str: Weight.
        """
        return str(self._weight.tag)

    def check_weight_input(self):
        """Function to manage validity of 'kind' input attribute via Mark class."""
        if not self._weight.tag.isdigit():
            message = (
                f"Invalid weight value, expected a number, "
                f"got {self._weight.tag}."
            )
            self._weight.isvalid = False
            self._weight.msg = message

    @property
    def video_url(self) -> Union[str, None]:
        """Video url: concats base_url and id.

        Returns:
            str: video_url

        """
        return f"{self.base_url}/{quote(self._id)}" if self.base_url else None

    @property
    def focus_pts(self) -> int:
        """Number of points the primary wrestler scored.

        Returns:
            int: Focus points scored

        """
        return self.calculate_pts("f")

    @property
    def opp_pts(self):
        """Number of points the opponent wrestler scored.

        Returns:
            int: Opponent points scored

        """
        return self.calculate_pts("o")

    @property
    def mov(self) -> int:
        """Margin of Victory.

        Returns:
            int: Difference between focus_points and opponent_points

        """
        return self.focus_pts - self.opp_pts

    @property
    def td_diff(self) -> int:
        """Takedown differential.

        Returns:
            int: Difference in primary wrestler takedowns and opponent takedowns

        """
        counts = Counter((score.formatted_label for score in self.time_series))
        return counts.get('fT2', 0) - counts.get('oT2', 0)

    def set_validity(self) -> bool:
        """Identifies instance validity status.

        This method returns boolean and is used in the attrs post_init hook to set the
        instance 'isvalid' attribute. However, this method also sets the instance
        'invalid_messages' and 'invalid_count' attributes according to the errors it
        detects when searching the instance.

        Any errors detected are input as brief descriptors into the
        'invalid_messages' attribute of the instance.

        The 'invalid_counts' is simply a count of how many errors were discovered.

        Returns:
            bool: True if all Marks are valid, else False (if any Marks are invalid).

        """
        messages = []
        status = True
        if isinstance(self._weight, base.Mark) and not self._weight.isvalid:
            messages.append("Invalid weight class.")
            status = False
        if not all((score.label.isvalid for score in getattr(self, "time_series"))):
            messages.append("Invalid time-series label.")
            status = False
        if isinstance(self.event._kind, base.Mark) and not self.event._kind.isvalid:
            messages.append("Invalid event type.")
            status = False
        self.invalid_messages = tuple(messages)
        self.invalid_count = len(messages)
        return status

    def calculate_pts(self, athlete_filter: str) -> int:
        """Calculate total points scored.

        Args:
            athlete_filter: 'f' or 'o'  to filter by 'focus' or 'opponent'

        Returns:
            int: Sum of points scored.

        """
        return sum(
            (
                action.label.point_value
                for action in getattr(self, "time_series")
                if action.formatted_label.startswith(athlete_filter)
            )
        )

    def to_dict(
            self, ts_only: Optional[bool] = False, results_only: Optional[bool] = False
    ) -> Union[Dict, Tuple]:
        """Converts instance to dict representation.

        Args:
            ts_only: If you only want the time_series of the instance. Defaults to False.
            results_only: If you only want the results of the instance. Defaults to False.

        Returns:
            Dict[str, Union[str, int]]: Dictionary of instance values.

        """
        if ts_only:
            ts = tuple(
                dict(
                    x.to_dict(),
                    **dict(
                        focus_name=getattr(self, "focus").name,
                        opp_name=getattr(self, "opponent").name,
                        event_name=getattr(self, "event").name,
                    ),
                )
                for x in getattr(self, "time_series")
            )
            return ts
        elif results_only:
            result = getattr(self, "result").text
            binary, method = result.split()
            return dict(binary=binary, method=method)
        else:
            return dict(
                focus_name=getattr(self, "focus").name,
                focus_team=getattr(self, "focus").team,
                opp_name=getattr(self, "opponent").name,
                opp_team=getattr(self, "opponent").team,
                weight=getattr(self, "weight"),
                event_name=getattr(self, "event").name,
                event_type=getattr(self, "event").kind,
                date=str(getattr(self, 'date')),
                text_result=getattr(self, "result").text,
                num_result=getattr(self, "result").value,
                duration=getattr(self, "duration"),
                overtime=getattr(self, "overtime"),
                video=getattr(self, "video_url"),
                win=getattr(self, "result").win,
                bonus=getattr(self, "result").bonus,
                pin=getattr(self, "result").pin,
                team_pts=getattr(self, "result").team_points,
                focus_pts=getattr(self, "focus_pts"),
                opp_pts=getattr(self, "opp_pts"),
                mov=getattr(self, "mov"),
                td_diff=getattr(self, "td_diff"),
            )


@attr.s(slots=True, order=True, eq=True, kw_only=True, auto_attribs=True)
class CollegeMatch(Match):
    """Match for college ruleset.

    Args:
        duration (Optional[int]): Length of match, defaults to 420.
        time_series (Tuple([CollegeScoring])): sequence of scoring events.

    Raises:
        TypeError: All items in time_series must be CollegeScoring instances.
        ValueError: time_series must be sorted chronologically.

    """

    duration: Optional[int] = attr.ib(default=420, validator=instance_of(int))
    # auto sorts (based on time)
    time_series: Tuple[CollegeScoring] = attr.ib(
        validator=instance_of(Tuple), order=False, repr=lambda x: f"{len(x)} actions"
    )

    def __attrs_post_init__(self):
        """Post init function to call Mark input handlers from super-class."""
        Match.__attrs_post_init__(self)
        self.add_college_ts_points()

    @time_series.validator
    def check_time_series(self, attribute, value):
        """Validates that all time_series are of the correct type and in the correct order."""
        if not all(isinstance(event, CollegeScoring) for event in value):
            raise TypeError(
                f"All of the items in the `time_series` set must be "
                f"`CollegeScoring` objects."
            )
        if not isvalid_sequence("college", value):
            raise ValueError(f"Time series sequence appears invalid...")
    
    def add_college_ts_points(self):
        for i, score in enumerate(self.time_series):
            if i == 0:
                if score.formatted_label.startswith('f'):
                    self.time_series[i].focus_score = self.time_series[i].label.point_value
                    self.time_series[i].opp_score = 0
                elif score.formatted_label.startswith('o'):
                    self.time_series[i].focus_score = 0
                    self.time_series[i].opp_score = self.time_series[i].label.point_value
                continue
            if score.formatted_label.startswith('f'):
                self.time_series[i].focus_score = self.time_series[i].label.point_value + \
                                            self.time_series[i - 1].focus_score
                self.time_series[i].opp_score = self.time_series[i - 1].opp_score
            elif score.formatted_label.startswith('o'):
                self.time_series[i].focus_score = self.time_series[i - 1].focus_score
                self.time_series[i].opp_score = self.time_series[i].label.point_value + self.time_series[i - 1].opp_score
            else:
                raise ValueError(
                    f"Invalid `formatted_label`, expected startswith = 'o' or 'f', "
                    f"got {score.formatted_label!r}")
        ts = list(self.time_series)
        ts.insert(
            0,
            CollegeScoring(
                time_stamp=str(time(hour=0, minute=0, second=0)),
                initiator='red',
                focus_color='red',
                period=1,
                label=base.CollegeLabel('START')
            )
        )
        self.time_series = tuple(ts)
        return True


@attr.s(slots=True, order=True, eq=True, kw_only=True, auto_attribs=True)
class HSMatch(Match):
    """Match for college ruleset.

    Args:
        duration (Optional[int]): Length of match, defaults to 360.
        time_series (Tuple([HSScoring])): sequence of scoring events.

    Raises:
        TypeError: All items in time_series must be HSScoring instances.
        ValueError: time_series must be sorted chronologically.

    """

    duration: Optional[int] = attr.ib(default=360, validator=instance_of(int))
    # auto sorts (based on time)
    time_series: Tuple[HSScoring] = attr.ib(
        order=False, repr=lambda x: f"{len(x)} actions"
    )

    def __attrs_post_init__(self):
        """Post init function to call Mark input handlers from super-class."""
        Match.__attrs_post_init__(self)
        self.add_hs_ts_points()

    @time_series.validator
    def check_time_series(self, attribute, value):
        """Validates that all time_series are of the correct type and in the correct order."""
        if not all(isinstance(event, HSScoring) for event in value):
            raise TypeError(
                f"All of the items in the `time_series` set must be "
                f"`HighSchoolScoring` objects."
            )
        if not isvalid_sequence("high school", value):
            raise ValueError(f"Time series sequence appears invalid...")

    def add_hs_ts_points(self):
        for i, score in enumerate(self.time_series):
            if i == 0:
                if score.formatted_label.startswith('f'):
                    self.time_series[i].focus_score = self.time_series[i].label.point_value
                    self.time_series[i].opp_score = 0
                elif score.formatted_label.startswith('o'):
                    self.time_series[i].focus_score = 0
                    self.time_series[i].opp_score = self.time_series[i].label.point_value
                continue
            if score.formatted_label.startswith('f'):
                self.time_series[i].focus_score = self.time_series[i].label.point_value + \
                                            self.time_series[i - 1].focus_score
                self.time_series[i].opp_score = self.time_series[i - 1].opp_score
            elif score.formatted_label.startswith('o'):
                self.time_series[i].focus_score = self.time_series[i - 1].focus_score
                self.time_series[i].opp_score = self.time_series[i].label.point_value + self.time_series[i - 1].opp_score
            else:
                raise ValueError(
                    f"Invalid `formatted_label`, expected startswith = 'o' or 'f', "
                    f"got {score.formatted_label!r}")
        ts = list(self.time_series)
        ts.insert(
            0,
            HSScoring(
                time_stamp=str(time(hour=0, minute=0, second=0)),
                initiator='red',
                focus_color='red',
                period=1,
                label=base.HSLabel('START')
            )
        )
        self.time_series = tuple(ts)
        return True
