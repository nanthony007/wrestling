#! /usr/bin/python

"""Module for Events.

This module builds the Events class with validation for its fields. When
validation is stronger than simple type validation, the Mark class is used
in replace of traditional str or int classes to track accuracy.

Example:
    event = Event(name='Practice', kind=Mark('Dual Meet'))

"""

from typing import Dict

import attr
from attr.validators import instance_of

from wrestling import base


def convert_event_name(name: str) -> str:
    """Strips and capitalizes a string.

    This function takes a string input and, if the string length is larger than 1,
    capitalized the string and strips leading/trailing whitespaces.

    Args:
        name: Any string of any length.

    Returns:
        str: Capitalized and stripped string.

    """
    if len(name) == 0:
        return "Generic Event"
    return name.title().strip()


@attr.s(auto_attribs=True, order=False, eq=True, slots=True)
class Event(object):
    """Class for storing event related data.

    Args:
        name (str): Name of the event.
        kind (str): Type of event, either 'Dual Meet' or 'Tournament'.

    """

    name: str = attr.ib(converter=convert_event_name, validator=instance_of(str))
    _kind: base.Mark = attr.ib(
        validator=instance_of(base.Mark), repr=lambda x: x.tag, eq=False,
    )

    def __attrs_post_init__(self):
        """Post init function to call Mark input handlers."""
        self.type_input_handler()

    @property
    def kind(self) -> str:
        """Type of event.

        Returns:
            str: Type of event.

        """
        return str(self._kind.tag)

    def type_input_handler(self) -> None:
        """Function to manage validity of 'kind' input attribute via Mark class."""
        if self._kind.tag not in {"Tournament", "Dual Meet"}:
            message = (
                f'Invalid Event type, expected one of "Tournament", '
                f'"Dual Meet", got {self._kind.tag}.'
            )
            self._kind.isvalid = False
            self._kind.msg = message

    def to_dict(self) -> Dict[str, str]:
        """Creates a dictionary representation of an Event instance.

        Returns:
            Dict: Dictionary with the name and kind of the Event instance.

        """
        return dict(name=self.name, kind=self.kind, )
