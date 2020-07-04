#!/usr/bin/env python
# coding: utf-8


"""
NAME
    API Parsing

DESCRIPTION
    This module contains all functions for accessing MatBoss data.

FUNCTIONS
    get_focus(match)
        Returns focus of match.

    parse_name(match, color)
        Returns wrestler name.

    parse_team(match, color)
        Returns team name.

    parse_results(match, user_level)
        Returns match result information.

    parse_demographics(match, event_list)
        Returns match demographic information.

    calculate_seconds(action_dict)
        Returns seconds.

    generate_event_label(action_dict)
        Returns event label.

    generate_pretty_time(action_dict)
        Returns time of event.

    label_period(secs)
        Returns period.

    clean_timeseries(action_dict, demo)
        Returns only needed timeseries values.

    parse_action_values(match, mode)
        Returns list of clean timeseries dicts and label counter.

    add_timeseries_points(action_dicts, demo)
        Returns timeseries with points.
"""

import re
from collections import Counter, namedtuple
from datetime import datetime
from typing import List, Tuple, Optional, Dict
from uuid import uuid4
import urllib


def get_focus(match: Dict) -> str:
    """Determines Focus for match (based on user) from match object instance.

    Args:
        match: Match object instance.

    Returns:
        Color of focus (red or green).
    """
    red = match["redWrestler"]
    green = match["greenWrestler"]
    if red[0].isdigit():
        return "red"
    elif green[0].isdigit():
        return "green"
    else:
        return str()


def parse_name(match: Dict, color: str) -> str:
    """Parses wrestler string from match object instance.

    Args:
        match: Match object instance.
        color: Options: 'red' or 'green'.
    Returns:
        Wrestler name formatted Last, First.
    """
    regex_search = r"#(.*?)#"
    if color == "red":
        # Not flipped to save time
        name = re.findall(regex_search, match["redWrestler"])[0].split(',')
        return f"{name[0].strip()}, {name[1].strip()}" if len(name) > 1 else None
    elif color == "green":
        name = re.findall(regex_search, match["greenWrestler"])[0].split(',')
        return f"{name[0].strip()}, {name[1].strip()}" if len(name) > 1 else None


def parse_team(match: Dict, color: str) -> str:
    """Parses team name from match object instance.

    Args:
        match: Match object instance.
        color: Options: 'red' or 'green'.

    Returns:
        Team name.
    """
    regex_search = r"#(.*?)#"
    if color == "red":
        # Not flipped to save time
        # Last, First
        team = re.findall(regex_search, match["redWrestler"])[1]
        if "(" in team:
            return team.split("(")[0]
        return team
    elif color == "green":
        team = re.findall(regex_search, match["greenWrestler"])[1]
        if "(" in team:
            return team.split(" (")[0]
        return team


def parse_results(match: Dict, user_level: str) -> Dict:
    """Parses results from match object instance.

    Args:
        match: Match object instance.
        user_level: AgeLevel of user account from api login.
            Options: College Men, College Women, High School Boys, High School Girls, Middle School and Youth.

    Returns:
        Result info dict.
    """
    binary_result = match["winner"]
    unparsed_result = match["theResult"]
    max_match_length = 420 if "College" in user_level else 360

    if unparsed_result.startswith("Dec"):
        result = "Decision"
    elif unparsed_result.startswith("Dis"):
        result = "Disqualification"
    elif unparsed_result.startswith("Def"):
        result = "Default"
    elif unparsed_result.startswith("Maj"):
        result = "Major"
    elif unparsed_result.startswith("Tech"):
        result = "Tech"
    elif unparsed_result.startswith("Fall"):
        result = "Fall"
    elif unparsed_result.startswith("For"):
        result = "Forfeit"
    else:
        result = str()

    if result == "Decision" or result == "Major":
        duration = max_match_length
    elif result == "Tech":
        d = (
            match["scoringEvents"].split("#")[-1].split("*")[:2]
        )  # gets last scoringEvent
        duration = int(d[0]) * 60 + int(d[1]) if len(d[0]) < 0 else int()
    elif result == "Fall":
        d = unparsed_result.split(" ")[1].split(":")
        duration = int(d[0]) * 60 + int(d[1]) if len(d[0]) < 0 else int()
    elif result == "Disqualification" or result == "Default" or result == "Forfeit":
        duration = 0
    else:
        duration = int()

    return {
        "result": "Win" if binary_result == 1 else "Loss",
        "method": result,
        "overtime": True if "(" in unparsed_result else False,
        "duration": duration,
        "team_points": match.get("teamPoints") if binary_result == 1 else 0,  # 0 if loss
        "text_result": f"{'Win' if binary_result == 1 else 'Loss'}-{result}",
    }


def parse_demographics(match: Dict, event_list: List[Dict], userinfo: Dict) -> Dict:
    """Parses demographic preprocessing from match object instance.

    Args:
        match: Match object instance.
        event_list: List of event dicts.

    Returns:
        Dict of demographic info.
    """
    focus_color = get_focus(match)
    red_name = parse_name(match, "red")
    red_team = parse_team(match, "red")
    green_name = parse_name(match, "green")
    green_team = parse_team(match, "green")
    match_id_api = match["matchID"]
    match_time = (
        datetime.strptime(match_id_api[-25:-6], "%Y-%m-%d %H:%M:%S")
        if "+" in match_id_api
        else datetime.strptime(match_id_api[-19:], "%Y-%m-%d %H:%M:%S")
    )

    event_info = next(
        (event for event in event_list if event["id"] == match["eventID"]), None
    )

    if focus_color == "red":
        focus = red_name
        focus_team = red_team
        opponent = green_name
        opponent_team = green_team
    elif focus_color == "green":
        focus = green_name
        focus_team = green_team
        opponent = red_name
        opponent_team = red_team
    else:
        focus = str()
        focus_team = str()
        opponent = str()
        opponent_team = str()

    video_url = f"https://users.matbossapp.com/#/match/{urllib.parse.quote(match_id_api)}"

    return {
        "match_id": uuid4().hex,
        "focus_name": focus,
        "opp_name": opponent,
        "focus_team": focus_team,
        "opp_team": opponent_team,
        "date": datetime.strptime(match["theDate"], "%Y-%m-%d").date(),
        "timestamp": match_time,
        "weight_class": match.get("theWeightClass"),
        "scorebook": match_id_api.split(":")[2],
        "focus": focus_color,  # Used to keep track when linking timeseries
        "event": event_info["name"] if event_info else None,
        "event_type": event_info["type"] if event_info else None,
        "video_url": video_url,
    }


def calculate_seconds(action_dict: Dict) -> int:
    """Calculates seconds event happened at.

    Args:
        action_dict: Timeseries action namedtuple.

    Returns:
        Seconds as integer.
    """
    try:
        return int(action_dict["minute"]) * 60 + int(action_dict["second"])
    except ValueError:
        return int()


def generate_event_label(action_dict: Dict, focus: str) -> str:
    """Generates event label.

    Args:
        action_dict: Timeseries dict.
        focus: Match focus from demographics.

    Returns:
        String of event label.
    """
    event = action_dict["color"].lower() + "_" + action_dict["symbol"] if action_dict.get('color') else action_dict["symbol"]
    if focus == "green":
        return event.replace("red", "opp").replace("green", "focus")
    elif focus == "red":
        return event.replace("red", "focus").replace("green", "opp")
    else:  # BAD
        return str()


def generate_pretty_time(action_dict: Dict) -> str:
    """Generates 'pretty' event time for display.

    Args:
        action_dict: Timeseries action namedtuple.

    Returns:
        Time of event formatted 00:00 (min:sec).
    """
    minute = int(action_dict["minute"])
    try:
        second = int(action_dict["second"])
    except ValueError:
        second = int()
    return f"{minute:02}:{second:02}"


def label_period(secs: int) -> int:
    """Determines period based on seconds field.

    Args:
        secs: Seconds field from action_tuple namedtuple.

    Returns:
        Period event happened in. 4 if overtime.
    """
    if 0 <= secs <= 180:
        period = 1
    elif 180 < secs <= 300:
        period = 2
    elif 300 < secs <= 420:
        period = 3
    elif secs > 420:
        period = 4
    else:  # security
        period = 0
    return period


def clean_timeseries(action_dict: Dict, demo: Dict) -> Dict:
    """Extends timeseries for one event with more fields.

    Args:
        action_dict: Timeseries action dict.
        demo: Demographic preprocessing dictionary from parse_demographics().

    Returns:
        New timeseries dict.
    """
    ts_dict = dict()
    focus = demo["focus"]

    ts_dict["match_id"] = demo["match_id"]
    ts_dict["focus_name"] = demo["focus_name"]
    ts_dict["opp_name"] = demo["opp_name"]
    ts_dict["seconds"] = calculate_seconds(action_dict)
    ts_dict["period"] = label_period(ts_dict["seconds"])
    ts_dict["event_label"] = generate_event_label(action_dict, focus)
    ts_dict["event_time"] = generate_pretty_time(action_dict)
    return ts_dict


def parse_action_values(
    match: Dict, demo: Dict, mode: Optional[str] = "BASE", user_level='College'
) -> Tuple[List[Dict], Counter]:
    """Parses action labels and counts from match object instance.
    Returns dictionary of labels with value counts AND nested list of timeseries.

    Args:
        match: Match object instance.
        demo: Demographics dictionary
        mode: Method of analysis. Options: 'BASE' or 'ANALYTICS'.
        user_level: User AgeLevel.

    Returns:
        Tuple containing dict of label counts and list of timeseries namedtuples.
    """
    
    valid_base_labels = [
        "T2",
        "E1",
        "R2",
        "N2",
        "N4",  # Scoring, N5 and N3 not included, should be recorded as penalty
        "P1",
        "P2",
        "C",
        "WS",
        "S1",
        "S2",
        "RO1",  # Penalties and RT 
        "BOT",
        "TOP",
        "NEU",
        "DEFER",  # Choices
    ] if 'College' in user_level else [
        "T2",
        "E1",
        "R2",
        "N2",
        "N3",
        "P1",
        "P2",
        "C",
        "WS",
        "S1",
        "S2",  # Penalties 
        "BOT",
        "TOP",
        "NEU",
        "DEFER",  # Choices 
    ]

    valid_analytics_labels = ["HIa"]  # Needs expanded but here as placeholder

    Action = namedtuple("Action", ["minute", "second", "period", "symbol", "color"])

    focus = get_focus(match)

    actions = []
    actions.append(Action._make(["0", "0", "0", "START", ""]))

    for event in match["scoringEvents"].split("#"):
        if len(event.split('*')) != 5 or len(event.split('*')[0]) == 0:  # Checks for empty scoringEvents field
            return list(), Counter()

        if mode == "BASE":
            # Exclude if not valid label
            if event.split("*")[3] not in valid_base_labels:
                return list(), Counter()

        if mode == "ANALYTICS":
            # Exclude if not valid label
            if event.split("*")[3] not in valid_analytics_labels:
                return list(), Counter()

        actions.append(Action._make([e for e in event.split("*")]))

    action_counts = Counter(
        [
            "focus_" + a.symbol if a.color.lower() == focus else "opp_" + a.symbol
            for a in actions
        ]
    )
    actions_dicts = [clean_timeseries(action._asdict(), demo) for action in actions]
    return actions_dicts, action_counts


def add_timeseries_points(actions_dicts: List[Dict], user_level='College') -> List[Dict]:
    """Adds points for red/green to timeseries.

    Args:
        actions_dicts: Actions list of dicts from parse_action_values().

    Returns:
        New timeseries list of dicts with points.
    """
    move_points = {
        "T2": 2,
        "R2": 2,
        "E1": 1,
        "N2": 2,
        "N4": 4,  # College only
        "P1": 1,
        "P2": 2,
        "S1": 1,
        "S2": 2,
        "RO1": 1,  # College only
    } if 'College' in user_level else {
        "T2": 2,
        "R2": 2,
        "E1": 1,
        "N2": 2,
        "N3": 3,  
        "P1": 1,
        "P2": 2,
        "S1": 1,
        "S2": 2,
    }

    for i, event in enumerate(actions_dicts):
        if i == 0:  # First event
            actions_dicts[i]["opp"] = 0
            actions_dicts[i]["focus"] = 0
        else:  # All others
            label = event["event_label"].split("_")
            if label[0] == "focus":
                actions_dicts[i]["opp"] = actions_dicts[i - 1]["opp"]
                actions_dicts[i]["focus"] = actions_dicts[i - 1][
                    "focus"
                ] + move_points.get(label[1], 0)
            elif label[0] == "opp":
                actions_dicts[i]["focus"] = actions_dicts[i - 1]["focus"]
                actions_dicts[i]["opp"] = actions_dicts[i - 1]["opp"] + move_points.get(
                    label[1], 0
                )
    return actions_dicts
