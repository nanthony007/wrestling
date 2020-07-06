# module for eligibility/academic year enumerator

import enum


@enum.unique
class Year(enum.Enum):
	# values should be updated to reflect possible API changes or HS/College
	# differences
    FR = "Freshman"
    SO = "Sophomore"
    JR = "Junior"
    SR = "Senior"
