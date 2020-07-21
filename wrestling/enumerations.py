import aenum
import enum


# result section
class Result(enum.IntEnum):
    WIN_DECISION = 1
    WIN_MAJOR = 2
    WIN_TECH = 3
    WIN_FALL = 4
    LOSS_DECISION = -1
    LOSS_MAJOR = -2
    LOSS_TECH = -3
    LOSS_FALL = -4
    # anytime the match didn't fully end (disq, default, forfeit, inj, etc)
    NO_CONTEST = 0  # ask tyler about NC 

    @property
    def text(self):
        return " ".join([x for x in self.name.split("_")]).title()

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

    # get enum instance from base string w/ validation
    @classmethod
    def from_text(cls, result_text):
        if not isinstance(result_text, str):
            raise TypeError(f"Expected type str', got type {type(result_text)!r}.")
        if len(result_text.split()) != 2:
            raise ValueError(
                f"Expected two strings, ex: 'win fall', got {result_text!r}.")
        r1, r2 = result_text.split()
        if r1.lower() != 'win' and r1.lower() != 'loss':
            raise ValueError(
                f"Invalid binary result, expected one of 'win' or 'loss', got {r1!r}.")
        if r2.lower() not in {'decision', 'major', 'tech', 'fall'}:
            raise ValueError(
                f"Invalid method, expected one of 'decision', 'major', 'tech', 'fall', got {r1!r}.")
        # todo: add something for the default/disq (no-contest) here
        return cls[result_text.upper().replace(' ', '_')]


# eligibility section
@enum.unique
class Year(str, enum.Enum):
    FR = "Freshman"
    SO = "Sophomore"
    JR = "Junior"
    SR = "Senior"
    RS_FR = "Redshirt Freshman"
    RS_SO = "Redshirt Sophomore"
    RS_JR = "Redshirt Junior"
    RS_SR = "Redshirt Senior"
    HS_7 = "7"
    HS_8 = "8"
    HS_9 = "9"
    HS_10 = "10"
    HS_11 = "11"
    HS_12 = "12"


# labels section
class CollegeLabel(aenum.IntEnum, settings=aenum.NoAlias):
    # points section
    T2 = 2
    N2 = 2
    N4 = 4  # no N3 or N5, should be recorded as penalties
    E1 = 1
    R2 = 2
    # penalties section
    C = 0
    P1 = 1
    P2 = 2
    WS = 0
    S1 = 1
    S2 = 2
    RO1 = 1  # college only
    # choices section
    BOT = 0
    TOP = 0
    NEU = 0
    DEFER = 0


class HighSchoolLabel(aenum.IntEnum, settings=aenum.NoAlias):
    # points section
    T2 = 2
    N2 = 2
    N3 = 3  # no N4, should be recorded as penalties
    E1 = 1
    R2 = 2
    # penalties section
    C = 0
    P1 = 1
    P2 = 2
    WS = 0
    S1 = 1
    S2 = 2
    # choices section
    BOT = 0
    TOP = 0
    NEU = 0
    DEFER = 0
