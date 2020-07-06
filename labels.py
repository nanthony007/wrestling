# module for label enum classes

import enum


class CollegeLabel(enum.IntEnum):
	# points section
	T2 = 2
	NF2 = 2
	NF4 = 4  # no NF3 or NF5, should be recorded as penalties
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


class HighSchoolLabel(enum.IntEnum):
	# points section
	T2 = 2
	NF2 = 2
	NF3 = 3  # no NF4, should be recorded as penalties
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
	BOTTOM = 0
	TOP = 0
	NEUTRAL = 0
	DEFER = 0
