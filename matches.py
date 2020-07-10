# This file contains the data structures as for the project written as
# dataclasses as opposed to normal/standard classes
# Each structure has a Super class and then two subclasses, one for college
# and one for high school

import attr
from attr.validators import instance_of, in_

from typing import Optional, Union, Set
from datetime import datetime
from urllib.parse import quote
from collections import Counter


from valid_sequences import college_sequences, hs_sequences
from enumerations import Result, CollegeLabel
from events import Event
from scoring import CollegeScoring, HighSchoolScoring
from wrestlers import CollegeWrestler, HighSchoolWrestler


_college_weights = (125, 133, 141, 149, 157, 165, 174, 184, 197, 285)
_high_school_weights = (106, 113, 120, 126, 132, 138, 145, 152, 160, 170, 182, 195, 220, 285)


def _convert_ts(ts):
    # converts to sorted set
    return set(sorted(ts))


# todo: adjust validation to consider T2 -> S1 -> E1
# 3 step sequence, basically deal with penalties somehow to maintain state
# implement a focus_state variable inside this validator!?

# checks formatted label strings (fT2 or oE1)
# checks value and evaluates list of possible next values
def isvalid_sequence(level: str, val: str, next_val: str):
    if level == 'college':
        assert next_val in college_sequences[val], f'`next_val` not valid sequence. Expected one of: {college_sequences[val]}, got {val!r}.'
    elif level == 'high school':
        assert next_val in hs_sequences[val], f'`next_val` not valid sequence. Expected one of: {hs_sequences[val]}, got {val!r}.'
    else:
        raise ValueError(f'`Level` expected "college" or "high school", got {level!r}.')


@attr.s(frozen=True, slots=True, order=True, eq=True, kw_only=True, auto_attribs=True)
class Match(object):
    match_id: str = attr.ib(validator=instance_of(str), repr=False, order=False)
    # enter at your own risk
    base_url: Optional[Union[str, None]] = attr.ib(default=None, repr=False, order=False)  
    event: Event = attr.ib(validator=instance_of(Event), repr=lambda x: x.name, order=False)
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
    focus: CollegeWrestler = attr.ib(validator=instance_of(CollegeWrestler), order=False)
    opponent: CollegeWrestler = attr.ib(validator=instance_of(CollegeWrestler), order=False)
    weight_class: int = attr.ib(validator=[instance_of(int), in_(_college_weights)], order=False)
    # auto sorts (based on time)
    time_series: Set[CollegeScoring] = attr.ib(converter=_convert_ts, validator=instance_of(Set), order=False)

    @time_series.validator
    def _check_time_series(self, attrib, val):
        assert all(isinstance(event, CollegeScoring) for event in val), (
            "All of the items in the `time_series` set must be "
            "`CollegeScoring` objects."
        )
        # avoids last value in looping
        for i, score in enumerate(val[:-1]):
            assert score.time_stamp < val[i+1].time_stamp, f'Values in `time_series` appear to be sorted incorrectly.'
            isvalid_sequence('college', score.formatted_label, val[i+1].formatted_label)            


@attr.s(frozen=True, slots=True, order=True, eq=True, kw_only=True, auto_attribs=True)
class HighSchoolMatch(Match):
    focus: HighSchoolWrestler = attr.ib(validator=instance_of(HighSchoolWrestler), order=False)
    opponent: HighSchoolWrestler = attr.ib(validator=instance_of(HighSchoolWrestler), order=False)
    weight_class: int = attr.ib(validator=[instance_of(int), in_(_high_school_weights)], order=False)
    time_series: Set[HighSchoolScoring] = attr.ib(validator=instance_of(Set), order=False)

    # work on this, more strict
    @time_series.validator
    def _check_time_series(self, attrib, val):
        assert all(isinstance(event, HighSchoolScoring) for event in val), (
            "All of the items in the `time_series` set must be "
            "`HighSchoolScoring` objects."
        )

    @time_series.validator
    def _check_time_series(self, attrib, val):
        assert all(isinstance(event, HighSchoolScoring) for event in val), (
            "All of the items in the `time_series` set must be "
            "`HighSchoolScoring` objects."
        )
        # avoids last value in looping
        for i, score in enumerate(val[:-1]):
            assert score.time_stamp < val[i+1].time_stamp, f'Values in `time_series` appear to be sorted incorrectly.'
            isvalid_sequence('high school', score.formatted_label, val[i+1].formatted_label)            

