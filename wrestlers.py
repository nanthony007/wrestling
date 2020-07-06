# module for wrestler classes

import attr
from attr.validators import instance_of, in_
from eligibility import Year


# todo: add method for calculating all the athlete metrics! (diff shows in
#  college vs hs --> reason for subclasses)


@attr.s(kw_only=True, auto_attribs=True)
class Wrestler(object):
    """Super-class for Wrestler information and statistics."""

    # todo: add validation for name formatting
    name: str = attr.ib(validator=instance_of(str))
    eligibility: Year = attr.ib(
        converter=lambda x: x.value,
        validator=[instance_of(str), in_([y.value for y in Year])],
    )


@attr.s(kw_only=True, auto_attribs=True)
class CollegeWrestler(Wrestler):
    pass


@attr.s(kw_only=True, auto_attribs=True)
class HighSchoolWrestler(Wrestler):
    pass


print(Year)
print(Year("Freshman"))
print(Wrestler(name="Nick Anthony", eligibility=Year.SR))
print(CollegeWrestler(name="Nick Anthony", eligibility=Year.SR))
print(HighSchoolWrestler(name="Nick Anthony", eligibility=Year.SR))
