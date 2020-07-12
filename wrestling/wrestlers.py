# module for wrestler classes

from typing import Optional
import attr
from attr.validators import instance_of

from wrestling.enumerations import Year


# todo: add method for calculating all the athlete metrics! (should be in
#  college / hs --> reason for subclasses)
# should those metrics be abstract properties in the base class??


@attr.s(kw_only=True, auto_attribs=True)
class Wrestler(object):
    # todo: add validation for name formatting
    name: str = attr.ib(validator=instance_of(str))
    team: str = attr.ib(validator=instance_of(str))
    eligibility: Optional[Year] = attr.ib(
        validator=[instance_of(Year)],
        default=Year.FR
    )


@attr.s(kw_only=True, auto_attribs=True)
class CollegeWrestler(Wrestler):
    pass


@attr.s(kw_only=True, auto_attribs=True)
class HighSchoolWrestler(Wrestler):
    pass

# w1 = Wrestler(name="Nick Anthony", team='bluejays')
# print(w1)
# w2 = CollegeWrestler(name="Nick Anthony", team='bluejays', eligibility=Year.SR)
# w3 = HighSchoolWrestler(name="Nick Anthony", team='bluejays', eligibility=Year.SR)
# w4 = HighSchoolWrestler(name="Nick Anthony", team='bluejays', eligibility=Year.SR)
# print(w2 == w4)

# print(attr.asdict(w1))
