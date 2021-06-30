#! /usr/bin/python

"""Module for base classes and globals used throughout the project.

This module contains the Years dictionary, Result enumeration class,
the Mark class which is foundational to all other classes in the project,
and the CollegeLabel and HSLabel classes inheriting from the Mark class.

"""

import enum
from typing import Dict, Set, Union

import attr
from attr.validators import instance_of

YEARS = {
    -1: "Unknown",
    0: "K",
    1: "1st",
    2: "2nd",
    3: "3rd",
    4: "4th",
    5: "5th",
    6: "6th",
    7: "7th",
    8: "8th",
    9: "9th",
    10: "10th",
    11: "11th",
    12: "12th",
    13: "Fr.",
    15: "So.",
    17: "Jr.",
    19: "Sr.",
    14: "RS Fr.",
    16: "RS So.",
    18: "RS Jr.",
    20: "RS Sr.",

}
"""dict[int, str]: Module level variable containing string variants
of acceptable years of eligibility.

"""


class Result(enum.IntEnum):
    """Enumeration class for match Results.

    This class contains information on Results
    structured as an enumeration. There are additional properties
    for other metrics that can be identified based on the Result.

    Args:
        enum (IntEnum): IntEnum super class.

    Returns:
        name (str): String abbreviated representation of the result.
        value (int): Numeric representation of the result.

    """

    WD = 1
    WM = 2
    WT = 3
    WF = 4
    LD = -1
    LM = -2
    LT = -3
    LF = -4
    # anytime the match didn't fully end (disq, default, forfeit, inj, etc)
    NC = 0

    @property
    def text(self) -> str:
        """Expanded text representation of result.

        Returns:
            str: Full text of result.

        """
        text = ""
        if self.name == "NC":
            text = "No Contest"
        elif self.name == "WD":
            text = "Win Dec"
        elif self.name == "WM":
            text = "Win Major"
        elif self.name == "WT":
            text = "Win Tech"
        elif self.name == "WF":
            text = "Win Fall"
        elif self.name == "LD":
            text = "Loss Dec"
        elif self.name == "LM":
            text = "Loss Major"
        elif self.name == "LT":
            text = "Loss Tech"
        elif self.name == "LF":
            text = "Loss Fall"
        return text

    @property
    def win(self) -> bool:
        """Win or Loss.

        Returns:
            bool: True if Win, False if Loss.

        """
        return True if self.value > 0 else False

    @property
    def bonus(self) -> bool:
        """Identifies whether Result is considered bonus or not.

        Returns:
            bool: True if considered bonus, else False.

        """
        return True if self.value > 1 or self.value < -1 else False

    @property
    def pin(self) -> bool:
        """Identifies if Result is a pin variation.

        Returns:
            bool: True if method of result is Fall, else False.

        """
        return True if self.value == 4 else False

    @property
    def team_points(self) -> int:
        """Calculates team points earned based on Result.

        Returns:
            int: Number of team points earned.

        """
        if self.value == 1:
            val = 3
        elif self.value == 2:
            val = 4
        elif self.value == 3:
            val = 5
        elif self.value == 4:
            val = 6
        else:  # loss
            val = 0
        return val


@attr.s(auto_attribs=True, eq=False, order=False, slots=True)
class Mark(object):
    """Mark object which acts as a Meta class for str and int inputs.

    This class should be used whenever validation on a class field is
    stonger than simple type validation. Prompts will be provided for
    established classes.

    Args:
        tag String or Integer value for the Mark.
        isvalid: Whether tag is valid or invalid, default to True.
        msg: Message for tag, defaults to empty string, should be changed if isvalid
        is False.

    """

    tag: Union[str, int] = attr.ib()
    isvalid: bool = attr.ib(default=True, init=False, validator=instance_of(bool))
    msg: str = attr.ib(default="", init=False, repr=False, validator=instance_of(str))

    @tag.validator
    def check_tag(self, attribute, value):
        """Attrs based validator function for tag attribute.

        Raises:
            TypeError: TypeError if tag value is not int or str type.

        """
        if not isinstance(value, str) and not isinstance(value, int):
            raise TypeError(
                f"`tag` value must be of type 'int' or 'str', got {type()!r}."
            )


@attr.s(auto_attribs=True, order=False, eq=False, slots=True)
class CollegeLabel(Mark):
    """Label class for College scoring event labels.

    Args:
        point_value: Numeric point value for label, different than tag value.

    """

    point_value: int = attr.ib(init=False, repr=False)

    def __attrs_post_init__(self):
        """Post init hook function.

        This function checks if the label tag is considered a valid label based
        on college (folkstyle) ruleset.  If not it adjusts the 'isvalid' and 'msg'
        attributes accordingly.

        """
        if self.tag in self.valid_labels:
            self.point_value = self.points_dict[self.tag]
        else:  # invalid tag
            message = (
                f"Invalid tag for 'College Label'. Expected one of "
                f"{*self.valid_labels,}, got {self.tag}."
            )
            self.point_value = 0
            self.isvalid = False
            self.msg = message

    @property
    def valid_labels(self) -> Set:
        """Set of valid scoring event labels based on current college ruleset.

        Returns:
            Set: Scoring events.
        """
        return {
            "START",
            "T2",
            "E1",
            "R2",
            "N2",
            "N4",
            "C",
            "P1",
            "P2",
            "WS",
            "S1",
            "S2",
            "RT1",
            "BOT",
            "TOP",
            "NEU",
            "DEFER",
            "Fall",
            "Tech Fall",
            "Forfeit",
            "Default",
        }

    @property
    def points_dict(self) -> Dict:
        """Dictionary of valid scoring event labels and their point values.

        Returns:
            Dict: Dictionary of labels and their corresponding point values.
        """
        return {
            "START": 0,
            "T2": 2,
            "E1": 1,
            "R2": 2,
            "N2": 2,
            "N4": 4,
            "C": 0,
            "P1": 1,
            "P2": 2,
            "WS": 0,
            "S1": 1,
            "S2": 2,
            "RT1": 1,
            "BOT": 0,
            "TOP": 0,
            "NEU": 0,
            "DEFER": 0,
            "Fall": 0,
            "Tech Fall": 0,
            "Forfeit": 0,
            "Default": 0,
        }


@attr.s(auto_attribs=True, order=False, eq=False, slots=True)
class HSLabel(Mark):
    """Label class for High School scoring event labels.

    Args:
        point_value: Numeric point value for label, different than tag value.

    """

    point_value: int = attr.ib(validator=instance_of(int), init=False, repr=False)

    def __attrs_post_init__(self):
        """Post init hook function.

        This function checks if the label tag is considered a valid label based
        on high school (folkstyle) ruleset.  If not it adjusts the 'isvalid' and 'msg'
        attributes accordingly.

        """
        if self.tag in self.valid_labels:
            self.point_value = self.points_dict[self.tag]
        else:  # invalid tag
            message = (
                f"Invalid tag for 'High School Label'. Expected one of "
                f"{*self.valid_labels,}, got {self.tag}."
            )
            self.point_value = 0
            self.isvalid = False
            self.msg = message

    @property
    def valid_labels(self) -> Set:
        """Set of valid scoring event labels based on current college ruleset.

        Returns:
            Set: Scoring events.
        """
        return {
            "START",
            "T2",
            "E1",
            "R2",
            "N2",
            "N3",
            "C",
            "P1",
            "P2",
            "WS",
            "S1",
            "S2",
            "BOT",
            "TOP",
            "NEU",
            "DEFER",
            "Fall",
            "Tech Fall",
            "Forfeit",
            "Default",
        }

    @property
    def points_dict(self) -> Dict:
        """Dictionary of valid scoring event labels and their point values.

        Returns:
            Dict: Dictionary of labels and their corresponding point values.
        """
        return {
            "START": 0,
            "T2": 2,
            "E1": 1,
            "R2": 2,
            "N2": 2,
            "N3": 3,
            "C": 0,
            "P1": 1,
            "P2": 2,
            "WS": 0,
            "S1": 1,
            "S2": 2,
            "BOT": 0,
            "TOP": 0,
            "NEU": 0,
            "DEFER": 0,
            "Fall": 0,
            "Tech Fall": 0,
            "Forfeit": 0,
            "Default": 0,
        }
