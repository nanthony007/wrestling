# This file contains the data structures as for the project written as
# dataclasses as opposed to normal/standard classes
# Each structure has a Super class and then two subclasses, one for college
# and one for high school


from dataclasses import dataclass, field, InitVar
from urllib.parse import quote
import re
from typing import Dict, List
from collections import Counter
from parse2 import *
from extend2 import *


@dataclass
class Match:
	# setting defaults for now
	hash_id: str = field(default=None, repr=False)
	match_id: InitVar[str] = None
	event_id: InitVar[str] = None
	date: str = ""  # datetime field
	timestamp: str = ""  # datetime field
	weight: int = 0
	actions: InitVar[str] = None  # scoring events from api
	winner: InitVar[int] = None  # 0 or 1 --> does this reflect the match focus
	# accurately?
	result: InitVar[str] = None
	team_pts: InitVar[int] = None
	red_wrestler: InitVar[str] = None
	green_wrestler: InitVar[str] = None

	focus_color: str = field(init=False)
	focus_name: str = field(init=False)
	opponent_name: str = field(init=False)
	focus_team: str = field(init=False)
	opponent_team: str = field(init=False)
	binary_result: bool = field(init=False)
	base_result: str = field(init=False)
	method: str = field(init=False)
	overtime: bool = field(init=False)
	team_points: int = field(init=False)
	text_result: str = field(init=False)
	video_url: str = field(init=False)  # formatted match_id, put above for now

	# extended stuff
	bonus: bool = field(init=False)
	pin: bool = field(init=False)

	# get these by comparing to event list (use event_id for comparison)
	event_name: str = ""
	event_type: str = ""

	# parse out actions
	time_series: list = field(default_factory=list, init=False)  # list of
	# ScoringEvents

	def __post_init__(
		self,
		match_id: str,
		event_id: str,
		actions: str,
		winner: str,
		result: str,
		team_pts: int,
		red_wrestler: str,
		green_wrestler: str,
	):
		# misses invalid color
		self.focus_color = "green" if green_wrestler[0].isdigit() else "red"
		self.focus_name = parse_name(
			green_wrestler if self.focus_color == "green" else red_wrestler
		)
		self.opponent_name = parse_name(
			red_wrestler if self.focus_color == "green" else green_wrestler
		)
		self.focus_team = parse_team(
			green_wrestler if self.focus_color == "green" else red_wrestler
		)
		self.opponent_team = parse_team(
			red_wrestler if self.focus_color == "green" else green_wrestler
		)
		self.video_url = f"https://users.matbossapp.com/#/match" f"/{quote(match_id)}"

		result_info = parse_results(winner, result, team_pts)
		self.base_result = result_info['base_result']
		self.binary_result = True if self.base_result == 'Win' else False
		self.method = result_info['method']
		self.overtime = result_info['overtime']
		self.team_points = result_info['team_points']
		self.text_result = result_info['text_result']

		self.bonus = (
			True
			if self.base_result == "Win" and self.method in ["Major", "Tech", "Fall"]
			else False
		)

		self.num_result = calculate_numeric_result(self.text_result)
		self.pin = True if self.num_result == 1.80 else 0

	# problem getting event_list into post_init
	# def get_event_info(self, event_id: str, event_list: List[Dict[str, str]]):
	# 	# needs return value if successful or failed
	# 	for event in event_list:
	# 		if event.get("eventID") == event_id:
	# 			self.event_name = event.get("eventName")
	# 			self.event_type = event.get("eventType")


@dataclass
class CollegeMatch(Match):
	# can put tests to specify acceptable weights and other values
	duration: int = 420  # add Meta to specify seconds

	focus_points: int = field(default=None, init=False)
	opp_points: int = field(default=None, init=False)
	mov: int = field(default=None, init=False)
	td_diff: int = field(default=None, init=False)

	def __post_init__(
		self,
		match_id: str,
		event_id: str,
		actions: str,
		winner: str,
		result: str,
		team_pts: int,
		red_wrestler: str,
		green_wrestler: str,
	):
		Match.__post_init__(
			self,
			match_id,
			event_id,
			actions,
			winner,
			result,
			team_pts,
			red_wrestler,
			green_wrestler,
		)
		self.time_series = generate_time_series(self, actions, 'college')
		self.add_ts_fields()
		self.focus_points = self.calculate_pts('focus')
		self.opp_points = self.calculate_pts('opp')
		self.mov = self.focus_points - self.opp_points
		self.td_diff = calculate_td_diff(self)
		add_ts_scoring(self, 'college')

	# does for focus/opp pts totals
	def calculate_pts(self, athlete_filter):
		pts = 0
		for field in dir(self):
			if field.startswith(athlete_filter) and field not in ['focus_color',
																  'focus_name',
																  'focus_team']:
				if field.endswith("1"):
					pts += getattr(self, field)
				if field.endswith("2"):
					pts += getattr(self, field) * 2
				if field.endswith("4"):
					pts += getattr(self, field) * 4
		return pts

	def add_ts_fields(self):
		counts = Counter([x.label for x in self.time_series])
		for col in counts.keys():
			setattr(self, col, counts[col])


@dataclass
class HighSchoolMatch(Match):
	duration: int = 360

	focus_points: int = field(default=None, init=False)
	opp_points: int = field(default=None, init=False)
	mov: int = field(default=None, init=False)
	td_diff: int = field(default=None, init=False)

	def __post_init__(
		self,
		match_id: str,
		event_id: str,
		actions: str,
		winner: str,
		result: str,
		team_pts: int,
		red_wrestler: str,
		green_wrestler: str,
	):
		Match.__post_init__(self)
		self.time_series = generate_time_series(self, actions, 'high_school')
		self.add_ts_fields()
		self.focus_points = self.calculate_pts('focus')
		self.opp_points = self.calculate_pts('opp')
		self.mov = self.focus_points - self.opp_points
		self.td_diff = calculate_td_diff(self)
		add_ts_scoring(self, 'high_school')

	# does for focus/opp pts totals
	def calculate_pts(self, athlete_filter):
		pts = 0
		for field in dir(self):
			if field.startswith(athlete_filter) and field not in ['focus_color',
																  'focus_name',
																  'focus_team']:
				if field.endswith("1"):
					pts += getattr(self, field)
				if field.endswith("2"):
					pts += getattr(self, field) * 2
				if field.endswith("3"):
					pts += getattr(self, field) * 3
		return pts

	def add_ts_fields(self):
		counts = Counter([x.label for x in self.time_series])
		for col in counts.keys():
			setattr(self, 'col', counts[col])


@dataclass
class ScoringEvent:
	focus: InitVar[str]
	minute: int = 0
	second: int = 0
	period: int = 0
	event: str = "START"
	owner: str = ""

	focus_score: int = field(init=False, default=0)
	opponent_score: int = field(init=False, default=0)

	formatted_period: int = field(init=False, default=0)
	label: str = field(init=False, default=None)
	seconds: int = field(init=False, default=None)
	formatted_time: str = field(init=False, default=None)

	def __post_init__(self, focus: str):
		self.label = self.format_label(focus)
		self.seconds = self.minute * 60 + self.second
		self.formatted_time = f"{self.minute:02}:{self.second:02}"
		self.formatted_period = label_period(self.seconds)

	def format_label(self, focus: str):
		event = f"{self.owner.lower()}_{self.event}" if self.owner else self.event
		if focus == "green":
			return event.replace("red", "opp").replace("green", "focus")
		elif focus == "red":
			return event.replace("red", "focus").replace("green", "opp")
		else:
			raise ValueError(focus)


@dataclass
class HighSchoolScoringEvent(ScoringEvent):
	# can put something to make sure event is allowed
	event: str = 'START'


@dataclass
class CollegeScoringEvent(ScoringEvent):
	event: str = 'START'


# @dataclass
# class AdvancedScoringEvent(ScoringEvent):
# 	event: str


# @dataclass
# class Wrestler:
# 	"""Super-class for Wrestler information and statistics."""
#
# 	name: str
# 	eligibility: str
#
#
# @dataclass
# class CollegeWrestler(Wrestler):
# 	"""Sub-class for college wrestler information and statistics."""
#
# 	near_fall4: int
# 	riding_time: int
#
#
# @dataclass
# class HighSchoolWrestler(Wrestler):
# 	"""Sub-class for high school wrestler information and statistics."""
#
# 	near_fall3: int
