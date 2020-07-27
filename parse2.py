from typing import Dict
import re


def get_focus(match: Dict) -> str:
	red = match["redWrestler"]
	green = match["greenWrestler"]
	if red.startswith(match['ourWrestler']):
		return "red"
	elif green.startswith(match['ourWrestler']):
		return "green"
	else:
		return str()


def parse_name(wrestler_string) -> str:
	regex_search = r"#(.*?)#"
	# Not flipped to save time
	name = re.findall(regex_search, wrestler_string)[0].split(",")
	return f"{name[0].strip()}, {name[1].strip()}" if len(name) > 1 else None


def parse_team(wrestler_string) -> str:
	regex_search = r"#(.*?)#"
	team = re.findall(regex_search, wrestler_string)[1]
	if "(" in team:
		return team.split("(")[0]
	return team
