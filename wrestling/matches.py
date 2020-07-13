# This file contains the data structures as for the project written as
# dataclasses as opposed to normal/standard classes
# Each structure has a Super class and then two subclasses, one for college
# and one for high school

import attr
from attr.validators import instance_of, in_

from typing import Optional, Union, Set
from datetime import datetime
from urllib.parse import quote

from wrestling.valid_sequences import college_sequences, hs_sequences
from wrestling.enumerations import Result
from wrestling.events import Event
from wrestling.scoring import CollegeScoring, HighSchoolScoring
from wrestling.wrestlers import Wrestler

_college_weights = (125, 133, 141, 149, 157, 165, 174, 184, 197, 285)
_high_school_weights = (
    106,
    113,
    120,
    126,
    132,
    138,
    145,
    152,
    160,
    170,
    182,
    195,
    220,
    285,
)


def _convert_ts(ts):
    # converts to sorted set
    return set(sorted(ts))


# checks formatted label strings (fT2 or oE1)
# checks value and evaluates list of possible next values
def isvalid_sequence(level: str, time_series: Tuple):
    assert level in {"college", "high school"}, (
        f"Expected `level` to be one of "
        f"'college' or 'high school', "
        f"got {level!r}."
    )
    # aliases sequences based on level
    sequences = college_sequences if level == "college" else hs_sequences
    position = "neutral"
    # skips iteration the last value because we check the next
    for i, score in enumerate(time_series[:-1]):
        assert (
                time_series[i].time_stamp < time_series[i + 1].time_stamp
        ), f"Values in `time_series` appear to be sorted incorrectly."
        lab = score.formatted_label
        if position == "neutral":
            assert lab in sequences["neutral"], (
                f"Not a valid neutral move, expected one of"
                f" {sequences['neutral']}, but got {lab}."
            )
            if lab == "fT2":
                position = "top"
            elif lab == "oT2":
                position = "bottom"
        elif position == "top":
            assert lab in sequences["top"], (
                f"Not a valid neutral move, expected one of"
                f" {sequences['top']}, but got {lab}."
            )
            if lab == "oE1":
                position = "neutral"
            elif lab == "oR2":
                position = "bottom"
        elif position == "bottom":
            assert lab in sequences["bottom"], (
                f"Not a valid neutral move, expected one of"
                f" {sequences['bottom']}, but got {lab}."
            )
            if lab == "fE1":
                position = "neutral"
            elif lab == "fR2":
                position = "top"
        else:
            raise ValueError(
                f"Invalid `position`, expected one of ['neutral', "
                f"'top', 'bottom'], got {position!r}."
            )
    return True


@attr.s(frozen=True, slots=True, order=True, eq=True, kw_only=True, auto_attribs=True)
class Match(object):
    match_id: str = attr.ib(validator=instance_of(str), repr=False, order=False)
    # enter at your own risk
    base_url: Optional[Union[str, None]] = attr.ib(
        default=None, repr=False, order=False
    )
    event: Event = attr.ib(
        validator=instance_of(Event), repr=lambda x: x.name, order=False
    )
    match_date: datetime = attr.ib(validator=instance_of(datetime), order=True)
    result: Result = attr.ib(validator=instance_of(Result), order=False)
    overtime: bool = attr.ib(validator=instance_of(bool), order=False)

    @match_id.validator
    def _check_match_id(self, attrib, val):
        if len(val) < 20 or len(val) > 50:
            raise ValueError(
                f"Expected str `match_id` with 20 <= len <= 50, " f'got "{val}"'
            )

    @overtime.validator
    def _check_overtime(self, attrib, val):
        # cannot tech in overtime
        if self.result == Result.WIN_TECH or self.result == Result.LOSS_TECH:
            assert val is False

    @property
    def video_url(self):
        return f"{self.base_url}/{quote(self.match_id)}" if self.base_url else None

    @property
    def focus_pts(self):
        return self._calculate_pts("f")

    @property
    def opp_pts(self):
        return self._calculate_pts("o")

    @property
    def mov(self):
        return self.focus_pts - self.opp_pts

    @property
    def td_diff(self):
        # default 0 if attribute not found
        return getattr(self, "fT2", 0) - getattr(self, "oT2", 0)

    # 'f' or 'o' filter
    def _calculate_pts(self, athlete_filter):
        return sum(
            (
                event.label.value
                for event in self.time_series
                if event.formatted_label.startswith(athlete_filter)
            )
        )


@attr.s(frozen=True, slots=True, order=True, eq=True, kw_only=True, auto_attribs=True)
class CollegeMatch(Match):
    focus: Wrestler = attr.ib(validator=instance_of(Wrestler), order=False)
    opponent: Wrestler = attr.ib(validator=instance_of(Wrestler), order=False)
    weight_class: int = attr.ib(
        validator=[instance_of(int), in_(_college_weights)], order=False
    )
    # auto sorts (based on time)
    time_series: Set[CollegeScoring] = attr.ib(
        converter=_convert_ts, validator=instance_of(Set), order=False
    )

    @time_series.validator
    def _check_time_series(self, attrib, val):
        assert all(isinstance(event, CollegeScoring) for event in val), (
            "All of the items in the `time_series` set must be "
            "`CollegeScoring` objects."
        )
        assert isvalid_sequence("college", tuple(val)) is True, (
            f"Time series sequence appears " f"invalid..."
        )


@attr.s(frozen=True, slots=True, order=True, eq=True, kw_only=True, auto_attribs=True)
class HighSchoolMatch(Match):
    focus: Wrestler = attr.ib(validator=instance_of(Wrestler), order=False)
    opponent: Wrestler = attr.ib(validator=instance_of(Wrestler), order=False)
    weight_class: int = attr.ib(
        validator=[instance_of(int), in_(_high_school_weights)], order=False
    )
    time_series: Set[HighSchoolScoring] = attr.ib(
        validator=instance_of(Set), order=False
    )

    @time_series.validator
    def _check_time_series(self, attrib, val):
        assert all(isinstance(event, HighSchoolScoring) for event in val), (
            "All of the items in the `time_series` set must be "
            "`HighSchoolScoring` objects."
        )
        assert isvalid_sequence("college", tuple(val)) is True, (
            f"Time series sequence appears " f"invalid..."
        )
