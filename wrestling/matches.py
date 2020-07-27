# This file contains the data structures as for the project written as
# dataclasses as opposed to normal/standard classes
# Each structure has a Super class and then two subclasses, one for college
# and one for high school

import attr
from attr.validators import instance_of, in_

from typing import Optional, Union, Set, Tuple
from datetime import datetime
from urllib.parse import quote

from wrestling.sequence import isvalid_sequence
from wrestling import base
from wrestling.events import Event
from wrestling.scoring import CollegeScoring, HSScoring
from wrestling.wrestlers import Wrestler


@attr.s(frozen=True, slots=True, order=True, eq=True, kw_only=True, auto_attribs=True)
class Match(object):
    _id: str = attr.ib(validator=instance_of(str), repr=False, order=False)
    # enter at your own risk
    base_url: Optional[Union[str, None]] = attr.ib(
        default=None, repr=False, order=False
    )
    event: Event = attr.ib(
        validator=instance_of(Event), repr=lambda x: x.name, order=False
    )
    date: datetime = attr.ib(validator=instance_of(datetime), order=True, repr=False)
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

    def __attrs_post_init__(self):
        self.check_weight_input()

    @_id.validator
    def check_id(self, attribute, value):
        if len(value) < 50 or len(value) > 120:
            raise ValueError(
                f"Expected str `id_` with 50 <= len <= 120, " f'got "{value}"'
            )

    @overtime.validator
    def check_overtime(self, attribute, value):
        # cannot tech in overtime
        if self.result == base.Result.WT or self.result == base.Result.LT:
            if value:  # if overtime is True
                raise ValueError(f"Overtime must be false if match resulted in Tech.")

    @property
    def weight(self):
        return self._weight.tag

    def check_weight_input(self):
        if not self._weight.tag.isdigit():
            message = (
                f"Invalid weight value, expected a number, "
                f"got {self._weight.tag!r}."
            )
            self._weight.isvalid = False
            self._weight.msg = message
            logger.info(message)

    @property
    def video_url(self):
        return f"{self.base_url}/{quote(self._id)}" if self.base_url else None

    @property
    def focus_pts(self):
        return self.calculate_pts("f")

    @property
    def opp_pts(self):
        return self.calculate_pts("o")

    @property
    def mov(self):
        return self.focus_pts - self.opp_pts

    @property
    def td_diff(self):
        # default 0 if attribute not found
        return getattr(self, "fT2", 0) - getattr(self, "oT2", 0)
    
    @property
    def isvalid(self):
        # match attrs, only weight
        if isinstance(self._weight, base.Mark):
            if not self._weight.isvalid:
                return False
        # ts attrs
        if not all((score.label.isvalid for score in self.time_series)):
            return False
        # event attrs
        if isinstance(self.event._kind, base.Mark):
            if not self.event._kind.isvalid:
                return False
        # wrestler attrs
        if isinstance(self.focus._grade, base.Mark):
            if not self.focus._grade.isvalid:
                return False
        if isinstance(self.opponent._grade, base.Mark):
            if not self.opponent._grade.isvalid:
                return False
        return True

    # 'f' or 'o' filter
    def calculate_pts(self, athlete_filter):
        return sum(
            (
                action.label.value
                for action in getattr(self, "time_series")
                if action.formatted_label.startswith(athlete_filter)
            )
        )

    # custom settings for TS bc we need to insert the names and the event name
    def to_dict(
            self, ts_only: Optional[bool] = False, results_only: Optional[bool] = False
    ):
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
                date=datetime.strftime(getattr(self, "date"), "%Y-%m-%d %H:%M:%S"),
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


@attr.s(frozen=True, slots=True, order=True, eq=True, kw_only=True, auto_attribs=True)
class CollegeMatch(Match):
    # seconds
    duration: Optional[int] = attr.ib(default=420, validator=instance_of(int))
    # auto sorts (based on time)
    time_series: Tuple[CollegeScoring] = attr.ib(
        validator=instance_of(Tuple), order=False, repr=lambda x: f"{len(x)} actions"
    )

    def __attrs_post_init__(self):
        Match.__attrs_post_init__(self)

    @time_series.validator
    def check_time_series(self, attribute, value):
        if not all(isinstance(event, CollegeScoring) for event in value):
            raise TypeError(
                f"All of the items in the `time_series` set must be "
                f"`CollegeScoring` objects."
            )
        if not isvalid_sequence("college", value):
            raise ValueError(f"Time series sequence appears invalid...")


@attr.s(frozen=True, slots=True, order=True, eq=True, kw_only=True, auto_attribs=True)
class HSMatch(Match):
    # seconds
    duration: Optional[int] = attr.ib(default=360, validator=instance_of(int))
    # auto sorts (based on time)
    time_series: Tuple[HSScoring] = attr.ib(
        order=False, repr=lambda x: f"{len(x)} actions"
    )

    def __attrs_post_init__(self):
        Match.__attrs_post_init__(self)

    @time_series.validator
    def check_time_series(self, attribute, value):
        if not all(isinstance(event, HSScoring) for event in value):
            raise TypeError(
                f"All of the items in the `time_series` set must be "
                f"`HighSchoolScoring` objects."
            )
        if not isvalid_sequence("high school", value):
            raise ValueError(f"Time series sequence appears invalid...")
