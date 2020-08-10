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
        grade (Union[Mark, None]): Grade/eligibility of the wrestler, default to None.

    """

    name: str = attr.ib(
        converter=convert_to_title, validator=instance_of(str), order=True
    )
    team: str = attr.ib(
        converter=convert_to_title, validator=instance_of(str), order=False
    )
    _grade: Optional[Union[base.Mark, None]] = attr.ib(
        default=None, order=False, eq=False,
    )

    def __attrs_post_init__(self):
        """Post init function to call Mark input handlers."""
        self.grade_input_handler()

    @property
    def grade(self) -> str:
        """Eligibility of athlete.

        Returns:
            str: Grade/Eligbility of athlete.
        """
        if self._grade:
            return str(self._grade.tag)
        return str(self._grade)

    def grade_input_handler(self) -> None:
        """Function to manage validity of 'grade' input attribute via Mark class."""
        if self._grade:
            if self._grade.tag not in base.YEARS:
                message = (
                    f"Invalid year, expected one of {*base.YEARS,}, "
                    f"got {self._grade.tag}."
                )
                self._grade.isvalid = False
                self._grade.msg = message

    def to_dict(self) -> Dict[str, str]:
        """Creates a dictionary representation of an Wrestler instance.

        Returns:
            Dict: Dictionary with the name, team, and grade of the Wrestler instance.

        """
        return dict(name=self.name, team=self.team, grade=self.grade)
