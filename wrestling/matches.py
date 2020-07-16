# This file contains the data structures as for the project written as
# dataclasses as opposed to normal/standard classes
# Each structure has a Super class and then two subclasses, one for college
# and one for high school

import attr
from attr.validators import instance_of, in_

import abc

from typing import Optional, Union, Set, Tuple
from datetime import datetime
from urllib.parse import quote

from wrestling.sequences import isvalid_sequence
from wrestling.enumerations import Result
from wrestling.events import Event
from wrestling.scoring import CollegeScoring, HighSchoolScoring
from wrestling.wrestlers import Wrestler

_college_weights = (
'125', '133', '141', '149', '157', '165', '174', '184', '197', '285')
_high_school_weights = (
    '106',
    '113',
    '120',
    '126',
    '132',
    '138',
    '145',
    '152',
    '160',
    '170',
    '182',
    '195',
    '220',
    '285',
)


# converts to sorted set
def _convert_ts(ts):
    return tuple(sorted(ts))


@attr.s(frozen=True, slots=True, order=True, eq=True, kw_only=True, auto_attribs=True)
class Match(object):
    id_: str = attr.ib(validator=instance_of(str), repr=False, order=False)
    # enter at your own risk
    base_url: Optional[Union[str, None]] = attr.ib(
        default=None, repr=False, order=False
    )
    event: Event = attr.ib(
        validator=instance_of(Event), repr=lambda x: x.name, order=False
    )
    date_: datetime = attr.ib(validator=instance_of(datetime), order=True,
                              repr=False)
    result: Result = attr.ib(validator=instance_of(Result), order=False, repr=lambda
        x: x.text)
    overtime: Optional[bool] = attr.ib(validator=instance_of(bool), order=False,
                                       repr=False, default=False)

    @id_.validator
    def _check_id_(self, attrib, val):
        if len(val) < 50 or len(val) > 120:
            raise ValueError(
                f"Expected str `id_` with 50 <= len <= 120, " f'got "{val}"'
            )

    @overtime.validator
    def _check_overtime(self, attrib, val):
        # cannot tech in overtime
        if self.result == Result.WIN_TECH or self.result == Result.LOSS_TECH:
            if val:  # if overtime is True
                raise ValueError(f"Overtime must be false if match resulted in Tech "
                                 f"Fall.")

    @property
    def video_url(self):
        return f"{self.base_url}/{quote(self.id_)}" if self.base_url else None

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
                for event in getattr(self, 'time_series')
                if event.formatted_label.startswith(athlete_filter)
            )
        )

    # custom settings for TS bc we need to insert the names and the event name for
    # analyses later
    def to_dict(self, time_series_only: Optional[bool] = False):
        if time_series_only:
            ts = tuple(
                dict(
                    x.to_dict(), **dict(
                        focus_name=getattr(self, 'focus').name,
                        opp_name=getattr(self, 'opponent').name,
                        event_name=getattr(self, 'event').name)
                ) for x in getattr(self, 'time_series')
            )
            return ts
        else:
            return dict(
                focus_name=getattr(self, 'focus').name,
                focus_team=getattr(self, 'focus').team,
                opp_name=getattr(self, 'opponent').name,
                opp_team=getattr(self, 'opponent').team,
                weight=getattr(self, 'weight_class'),
                event_name=getattr(self, 'event').name,
                event_type=getattr(self, 'event').type_,
                date=datetime.strftime(getattr(self, 'date_'), "%Y-%m-%d %H:%M:%S"),
                text_result=getattr(self, 'result').text,
                num_result=getattr(self, 'result').value,
                overtime=getattr(self, 'overtime'),
                video=getattr(self, 'video_url'),
                win=getattr(self, 'result').win,
                bonuns=getattr(self, 'result').bonus,
                pin=getattr(self, 'result').pin,
                team_pts=getattr(self, 'result').team_points,
                focus_pts=getattr(self, 'focus_pts'),
                opp_pts=getattr(self, 'opp_pts'),
                mov=getattr(self, 'mov'),
                td_diff=getattr(self, 'td_diff'),
            )


@attr.s(frozen=True, slots=True, order=True, eq=True, kw_only=True, auto_attribs=True)
class CollegeMatch(Match):
    focus: Wrestler = attr.ib(validator=instance_of(Wrestler), order=False,
                              repr=lambda x: x.name)
    opponent: Wrestler = attr.ib(validator=instance_of(Wrestler), order=False,
                                 repr=lambda x: x.name)
    weight_class: Union[int, str] = attr.ib(order=False, repr=True)
    # seconds
    duration: Optional[int] = attr.ib(default=420, validator=instance_of(int))
    # auto sorts (based on time)
    time_series: Tuple[CollegeScoring] = attr.ib(validator=instance_of(Tuple),
                                                 order=False,
                                                 repr=lambda x: f"{len(x)}events"
                                                 )

    @weight_class.validator
    def _check_weight_class(self, attrib, val):
        if not isinstance(val, str) and not isinstance(val, int):
            raise TypeError(f"Expected int or str, got {val!r} with type {type(val)}.")
        if val not in _college_weights:
            raise ValueError(f"Expected on of: {_college_weights!r}, but got {val!r}.")

    @time_series.validator
    def _check_time_series(self, attrib, val):

        if not all(isinstance(event, CollegeScoring) for event in val):
            raise TypeError(f"All of the items in the `time_series` set must be "
                            f"`CollegeScoring` objects.")
        if not isvalid_sequence("college", val):
            raise ValueError(f"Time series sequence appears invalid...")


@attr.s(frozen=True, slots=True, order=True, eq=True, kw_only=True, auto_attribs=True)
class HighSchoolMatch(Match):
    focus: Wrestler = attr.ib(validator=instance_of(Wrestler), order=False,
                              repr=lambda x: x.name)
    opponent: Wrestler = attr.ib(validator=instance_of(Wrestler), order=False,
                                 repr=lambda x: x.name)
    weight_class: int = attr.ib(
        validator=[instance_of(int), in_(_high_school_weights)], order=False
    )
    # seconds
    duration: Optional[int] = attr.ib(default=360, validator=instance_of(int))
    time_series: Tuple[HighSchoolScoring] = attr.ib(
        validator=instance_of(Tuple), order=False, repr=lambda x: f"{len(x)} actions"
    )

    @time_series.validator
    def _check_time_series(self, attrib, val):
        if not all(isinstance(event, HighSchoolScoring) for event in val):
            raise TypeError(f"All of the items in the `time_series` set must be "
                            f"`HighSchoolScoring` objects.")
        if not isvalid_sequence("college", val):
            raise ValueError(f"Time series sequence appears invalid...")
