# module for wrestler classes

from typing import Optional, Union
import attr
from attr.validators import instance_of
from wrestling import base
import logging

logging.basicConfig(filename='logfile.log')
logger = logging.getLogger('Wrestler')


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
    _year: Optional[Union[base.Mark, None]] = attr.ib(
        default=None, order=False, eq=False
    )

    def __attrs_post_init__(self):
        self.check_year_input()

    @property
    def year(self):
        if self.year:
            return self._year.tag
        return self._year

    def check_year_input(self):
        if self._year:
            if self._year.tag not in base.YEARS:
                message = f'Invalid year, expected one of {base.YEARS}, ' \
                          f'got {self._year.tag!r}.'
                self._year.isvalid = False
                self._year.msg = message
                logger.info(message)

    def to_dict(self):
        return dict(
            name=self.name,
            team=self.team,
            year=self.year
        )
