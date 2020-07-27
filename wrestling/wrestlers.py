# module for wrestler classes

from typing import Optional, Union
import attr
from attr.validators import instance_of
from wrestling import base


def convert_to_title(x: str):
    return x.title().strip()


# these all need to use Tag
@attr.s(kw_only=True, auto_attribs=True, order=True, eq=True)
class Wrestler(object):
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
        self.grade_input_handler()

    @property
    def grade(self):
        if self._grade:
            return self._grade.tag
        return self._grade

    def grade_input_handler(self):
        if self._grade:
            if self._grade.tag not in base.YEARS:
                message = f'Invalid year, expected one of {base.YEARS}, ' \
                          f'got {self._grade.tag!r}.'
                self._grade.isvalid = False
                self._grade.msg = message
                logger.info(message)

    def to_dict(self):
        return dict(
            name=self.name,
            team=self.team,
            grade=self.grade
        )
