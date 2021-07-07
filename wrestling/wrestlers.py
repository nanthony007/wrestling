#! /usr/bin/python

"""Module for creating Wrestler objects.

This module builds the Wrestler class with validation for its fields. When
validation is stronger than simple type validation, the Mark class is used
in replace of traditional str or int classes to track accuracy.

Example:
    wrestler = Wrestler(name='Anthony, Nick', team="Eagles", grade=Mark('Sr.'))

"""

from typing import Dict, Optional, Union

import attr
from attr.validators import instance_of

from wrestling import base


def convert_to_title(name: str) -> str:
    """Makes a string title-ized.

    Args:
        name: Any string.

    Returns:
        str: Capitalized and white-spaced stripped string.

    """
    return name.title().strip()


@attr.s(kw_only=True, auto_attribs=True, order=True, eq=True, frozen=True, slots=True)
class Wrestler(object):
    """Wrestler object.

    Args:
        name (str): Name of the wrestler. Ex: Last, First.
        team (str): Team the wrestler represents.
        grade (Union[int, None]): Grade/eligibility of the wrestler, default to None.

    """

    name: str = attr.ib(
        converter=convert_to_title, validator=instance_of(str), order=True
    )
    team: str = attr.ib(
        converter=convert_to_title, validator=instance_of(str), order=False
    )
    grade_int: int = attr.ib(
        default=-1, order=False, eq=False,
    )

    @property
    def grade_str(self) -> str:
        """Eligibility of athlete.

        Returns:
            str: Grade/Eligbility of athlete.
        """
        return base.YEARS.get(self.grade_int, '')

    def to_dict(self) -> Dict[str, str]:
        """Creates a dictionary representation of an Wrestler instance.

        Returns:
            Dict: Dictionary with the name, team, and grade of the Wrestler instance.

        """
        return dict(name=self.name, team=self.team, grade=self.grade_str)
