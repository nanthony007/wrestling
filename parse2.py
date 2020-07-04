#!/usr/bin/env python
# coding: utf-8

from typing import Dict
import re
import structures


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


def parse_results(winner: str, result: str, team_pts: int) -> Dict[str, str]:
    if result.startswith("Dec"):
        formatted_result = "Decision"
    elif result.startswith("Maj"):
        formatted_result = "Major"
    elif result.startswith("Tech"):
        formatted_result = "Tech"
    elif result.startswith("Fall"):
        formatted_result = "Fall"
    elif result.startswith("Dis"):
        formatted_result = "Disqualification"
    elif result.startswith("Def"):
        formatted_result = "Default"
    elif result.startswith("For"):
        formatted_result = "Forfeit"
    elif result.startswith("Double"):  # weird? double forfeift
        formatted_result = "Forfeit"
    else:
        raise ValueError(result)

    return {
        "base_result": "Win" if winner == 1 else "Loss",  # there are 2s for
        # double forfeits
        "method": formatted_result,
        "overtime": True if "(" in result else False,
        "team_points": team_pts if winner == 1 else 0,  # 0 if loss
        "text_result": f"{'Win' if winner == 1 else 'Loss'}-{formatted_result}",
    }


def calculate_numeric_result(text_result):
    if text_result == "Win-Decision" or text_result == "Win-Disqualification":
        return 1.20
    elif text_result == "Win-Major":
        return 1.40
    elif text_result == "Win-Tech":
        return 1.60
    elif text_result == "Win-Fall":
        return 1.80
    elif text_result == "Loss-Decision":
        return 0.80
    elif text_result == "Loss-Major":
        return 0.60
    elif text_result == "Loss-Tech":
        return 0.40
    elif text_result == "Loss-Fall" or text_result == "Loss-Disqualification":
        return 0.20
    elif text_result == "Loss-Default":
        return 1.00
    elif text_result == "Win-Default":
        return 1.00
    elif text_result == "Loss-Forfeit":
        return 1.00
    elif text_result == "Win-Forfeit":
        return 1.00
    else:
        raise ValueError(text_result)


def calculate_td_diff(obj):
    fT2 = 0
    oT2 = 0
    if 'focus_T2' in dir(obj):
        fT2 = obj.focus_T2
    if 'opp_T2' in dir(obj):
        oT2 = obj.opp_T2
    return fT2 - oT2


# can probably make global
def label_period(seconds):
    if 0 <= seconds <= 180:
        period = 1
    elif 180 < seconds <= 300:
        period = 2
    elif 300 < seconds <= 420:
        period = 3
    elif seconds > 420:
        period = 4
    else:  # security
        raise ValueError(seconds)
    return period


def add_ts_scoring(obj, level_toggle):
    # remove, possibly transition to subclasses
    move_points = (
        {
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
        if level_toggle == "high school"
        else {
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
        }
    )
    for i, se in enumerate(obj.time_series):
        if i == 0:
            continue
        label = se.label.split("_")
        if label[0] == "focus":
            obj.time_series[i].focus_score = obj.time_series[
                i - 1
            ].focus_score + move_points.get(se.event, 0)
            obj.time_series[i].opponent_score = obj.time_series[i - 1].opponent_score
        elif label[0] == "opp":
            obj.time_series[i].opponent_score = obj.time_series[
                i - 1
            ].opponent_score + move_points.get(se.event, 0)
            obj.time_series[i].focus_score = obj.time_series[i - 1].focus_score
        else:
            raise ValueError(label[0])


def generate_time_series(obj, actions, toggle):
    scoring_events = (
        [structures.HighSchoolScoringEvent(focus=obj.focus_color)]
        if toggle == "high_school"
        else [structures.CollegeScoringEvent(focus=obj.focus_color)]
    )
    if len(actions) == 0:
        return scoring_events
    for action in actions.split("#"):
        if action == "****" or action.split('*')[0] == 'NaN':
            continue  # skipping this error as its no event
        if len(action.split("*")) != 5 or len(action) == 0:
            if action == "0*0*0*Forfeit*Red0*0*0*Forfeit*Red":
                continue  # this is a storage error on John's side
            raise ValueError(
                f"Length of scoring event: {len(action)}. " f"Action: {action}"
            )

        action_dict = {
            "minute": int(action.split("*")[0]),
            "second": int(action.split("*")[1]),
            "period": int(action.split("*")[2]),
            "event": action.split("*")[3],
            "owner": action.split("*")[4],
        }
        new_event = (
            structures.HighSchoolScoringEvent(focus=obj.focus_color, **action_dict)
            if toggle == "high_school"
            else structures.CollegeScoringEvent(focus=obj.focus_color, **action_dict)
        )
        scoring_events.append(new_event)
    return scoring_events
