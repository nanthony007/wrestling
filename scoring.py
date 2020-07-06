# module for scoring event classes

import attr
from attr.validators import instance_of, in_
import datetime
from labels import CollegeLabel, HighSchoolLabel


#  subclasses declare labels and periods and validate against acceptable values
@attr.s(kw_only=True, auto_attribs=True, slots=True)
class ScoringEvent(object):
	# validate that hour = 0
	time_stamp: datetime.time = attr.ib(validator=instance_of(datetime.time),
										repr=False)
	focus_color: str = attr.ib(validator=[instance_of(str), in_(('green',
																'red'))],
							   repr=False)
	initiator: str = attr.ib(validator=[instance_of(str), in_(('green',
																'red'))],
							   repr=False)
	# can add validation to ensure correctly switched formatting
	formatted_time: str = attr.ib(init=False, validator=instance_of(str))

	def __attrs_post_init__(self):
		self.formatted_time = datetime.time.strftime(self.time_stamp, '%M:%S')


@attr.s(kw_only=True, auto_attribs=True, slots=True)
class CollegeScoringEvent(ScoringEvent):
	# validate that label is in CollegeLabel Enum -- > names and point values
	#  this pattern sets good precedent for custom matches/events later
	#  should be instance of CollegeLabel Enum
	label: CollegeLabel = attr.ib(validator=[instance_of(CollegeLabel),
											   in_(CollegeLabel)], repr=False)
	period: int = attr.ib(init=False, validator=[instance_of(int), in_(range(1,
																		 5))], repr=False)
	# add validation for formatting
	formatted_label: str = attr.ib(init=False, validator=instance_of(str), repr=True)

	def __attrs_post_init__(self):
		ScoringEvent.__attrs_post_init__(self)
		self._set_period()
		self._set_formatted_label()

	def _set_period(self):
		if self.time_stamp.minute < 3:
			self.period = 1
		elif 3 <= self.time_stamp.minute < 5:
			self.period = 2
		elif 5 <= self.time_stamp.minute <= 7:
			self.period = 3
		elif self.time_stamp.minute > 7:
			self.period = 4
		else:
			raise ValueError(self.time_stamp.minute)

	def _set_formatted_label(self):
		if self.focus_color == self.initiator:
			self.formatted_label = f"f{self.label.name}"
		elif self.focus_color != self.initiator:
			self.formatted_label = f"o{self.label.name}"
		else:
			raise ValueError(self.focus_color, self.initiator)


@attr.s(kw_only=True, auto_attribs=True)
class HighSchoolScoringEvent(ScoringEvent):
	# validate that label is in HighSchoolLabel Enum -- > names and point values
	#  this pattern sets good precedent for custom matches/events later
	#  should be instance of HighSchoolLabel Enum
	label: HighSchoolLabel = attr.ib(validator=[instance_of(HighSchoolLabel),
											   in_(HighSchoolLabel)], repr=False)
	# add validation for formatting
	formatted_label: str = attr.ib(init=False, validator=instance_of(str), repr=True)
	period: int = attr.ib(init=False, validator=[instance_of(int), in_(range(1,
																		 5))], repr=False)

	def __attrs_post_init__(self):
		ScoringEvent.__attrs_post_init__(self)
		self._set_period()
		self._set_formatted_label()

	def _set_period(self):
		if self.time_stamp.minute < 2:
			self.period = 1
		elif 2 <= self.time_stamp.minute < 4:
			self.period = 2
		elif 4 <= self.time_stamp.minute <= 6:
			self.period = 3
		elif self.time_stamp.minute > 6:
			self.period = 4
		else:
			raise ValueError(self.time_stamp.minute)

	def _set_formatted_label(self):
		if self.focus_color == self.initiator:
			self.formatted_label = f"f{self.label.name}"
		elif self.focus_color != self.initiator:
			self.formatted_label = f"o{self.label.name}"
		else:
			raise ValueError(self.focus_color, self.initiator)



sc = CollegeScoringEvent(time_stamp=datetime.time(minute=2, second=58),
						 focus_color='green', initiator='green',
						 label=CollegeLabel.RT1)
hs_sc = HighSchoolScoringEvent(time_stamp=datetime.time(minute=2, second=58),
							   focus_color='red', initiator='green',
						 label=HighSchoolLabel.NF3)
print(sc)
print(hs_sc)
print(sc.formatted_time)

x = [HighSchoolScoringEvent(time_stamp=datetime.time(minute=2, second=58),
							   focus_color='red', initiator='green',
						 label=HighSchoolLabel.NF3) for _ in range(10)]
# works bc NOT slots=True
x[0].pts = x[0].label.value * 2
print(x[0].pts)

# throws error bc slots=True
sc.pts = 12
