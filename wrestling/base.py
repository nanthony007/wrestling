import aenum
import enum
import attr
from attr.validators import instance_of
from typing import Union

# eligibility
YEARS = {"Fr.", "So.", "Jr.", "Sr.", 'RS Fr.', 'RS So.', 'RS Jr.', 'RS Sr.', '7', '8',
         '9', '10', '11', '12'}


# check attr.s and attr.ib params (slots, order, eq, etc.)
@attr.s(auto_attribs=True)
class Mark(object):
    tag: Union[str, int] = attr.ib()
    isvalid: bool = attr.ib(default=True, init=False, validator=instance_of(bool))
    msg: str = attr.ib(default='', init=False, validator=instance_of(str))

    @tag.validator
    def check_tag(self, attribute, value):
        if not isinstance(value, str) and not isinstance(value, int):
            raise TypeError(f"`tag` value must be of type 'int' or 'str', got "
                            f"{type(value)!r}.")


# result section
class Result(enum.IntEnum):
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
    def text(self):
        if self.name == 'NC':
            return "No Contest"
        elif self.name == 'WD':
            return 'Win Dec'
        elif self.name == 'WM':
            return 'Win Major'
        elif self.name == 'WT':
            return 'Win Tech'
        elif self.name == 'WF':
            return 'Win Fall'
        elif self.name == 'LD':
            return 'Loss Dec'
        elif self.name == 'LM':
            return 'Loss Major'
        elif self.name == 'LT':
            return 'Loss Tech'
        elif self.name == 'LF':
            return 'Loss Fall'

    @property
    def win(self):
        return True if self.value > 0 else False

    @property
    def bonus(self):
        return True if self.value > 1 or self.value < -1 else False

    @property
    def pin(self):
        return True if self.value == 4 else False

    @property
    def team_points(self):
        if self.value == 1:
            return 3
        elif self.value == 2:
            return 4
        elif self.value == 3:
            return 5
        elif self.value == 4:
            return 6
        else:  # loss
            return 0


class CollegeLabel(aenum.IntEnum, settings=aenum.NoAlias):
    # points
    T2 = 2
    N2 = 2
    N4 = 4  # no N3 or N5, should be recorded as penalties
    E1 = 1
    R2 = 2
    # penalties
    C = 0
    P1 = 1
    P2 = 2
    WS = 0
    S1 = 1
    S2 = 2
    RO1 = 1  # college only
    # choices
    BOT = 0
    TOP = 0
    NEU = 0
    DEFER = 0


class HighSchoolLabel(aenum.IntEnum, settings=aenum.NoAlias):
    # points
    T2 = 2
    N2 = 2
    N3 = 3  # no N4, should be recorded as penalties
    E1 = 1
    R2 = 2
    # penalties
    C = 0
    P1 = 1
    P2 = 2
    WS = 0
    S1 = 1
    S2 = 2
    # choices
    BOT = 0
    TOP = 0
    NEU = 0
    DEFER = 0
