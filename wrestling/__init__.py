"""This package is for wrestling statisics.

The data containers provided can be used to represent the
various aspects of a match including Wrestlers, Events,
Scoring Events, and Matches themselves.  These containers
can all be extended in the future for other styles or rulesets
in the future.

The only package requirement is attrs.

Important notes:
    Use Mark class when prompted (as validation will utilize the
    Mark class extended functionality.)

"""

from .base import Mark, CollegeLabel, HSLabel, Result
from .events import Event
from .matches import CollegeMatch, HSMatch
from .scoring import CollegeScoring, HSScoring
from .wrestlers import Wrestler
