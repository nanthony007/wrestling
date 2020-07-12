import aenum
import enum


# result section
@enum.unique
class Result(enum.IntEnum):
    WIN_DECISION = 1
    WIN_MAJOR = 2
    WIN_TECH = 3
    WIN_FALL = 4
    LOSS_DECISION = -1
    LOSS_MAJOR = -2
    LOSS_TECH = -3
    LOSS_FALL = -4

    @property
    def text(self):
        #  split string
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


# todo: values should be updated to reflect API diffs or HS/College diffs
# eligibility section
@enum.unique
class Year(enum.Enum):
    FR = "Freshman"
    SO = "Sophomore"
    JR = "Junior"
    SR = "Senior"


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
	RT1 = 1  # college only
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
