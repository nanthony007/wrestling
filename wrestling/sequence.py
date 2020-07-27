# this module contains the dicts for valid sequence of events

from typing import Tuple

_always = [
    "fBOT",
    "fTOP",
    "fNEU",
    "fDEFER",
    "oBOT",
    "oTOP",
    "oNEU",
    "oDEFER",
    "fC",
    "fP1",
    "fP2",
    "fWS",
    "fS1",
    "fS2",
    "oC",
    "oP1",
    "oP2",
    "oWS",
    "oS1",
    "oS2",
    "fRO1",
    "oRO1",
]
_college_focus_top = ["fN2", "fN4", "oE1", "oR2"]
_college_focus_bottom = ["oN2", "oN4", "fE1", "fR2"]
_college_neutral = ["fT2", "oT2"]

_hs_focus_top = ["fN2", "fN3", "oE1", "oR2"]
_hs_focus_bottom = ["oN2", "oN3", "fE1", "fR2"]
_hs_neutral = ["fT2", "oT2"]

COLLEGE_SEQUENCES = dict(
    neutral=set(_college_neutral + _always),
    top=set(_college_focus_top + _always),
    bottom=set(_college_focus_bottom + _always),
    always=set(_always),
)

HS_SEQUENCES = dict(
    neutral=set(_hs_neutral + _always),
    top=set(_hs_focus_top + _always),
    bottom=set(_hs_focus_bottom + _always),
    always=set(_always),
)


def check_neutral(score, seq):
    if score.formatted_label not in seq and (not score.formatted_label.endswith('Succ') or not score.formatted_label.endswith('Fail')):
        # invalid
        score.label.isvalid = False
        score.label.msg = f"Not a valid neutral move, expected one of {seq}, but got {score.formatted_label!r}."
        

def check_top(score, seq):
    if score.formatted_label not in seq and (not score.formatted_label.endswith('Succ') or not score.formatted_label.endswith('Fail')):
        # invalid
        score.label.isvalid = False
        score.label.msg =f"Not a valid top move, expected one of {seq}, but got {score.formatted_label!r}."
        
def check_bottom(score, seq):
    if score.formatted_label not in seq and (not score.formatted_label.endswith('Succ') or not score.formatted_label.endswith('Fail')):
        # invalid
        score.label.isvalid = False
        score.label.msg = f"Not a valid bottom move, expected one of {seq}, but got {score.formatted_label!r}."
        

# checks formatted label strings (fT2 or oE1)
# checks value and evaluates list of possible next values
def isvalid_sequence(level: str, time_series: Tuple):
    if level not in {"college", "high school"}:
        raise ValueError(
            f"Expected `level` to be one of "
            f"'college' or 'high school', "
            f"got {level!r}."
        )
    # aliases sequences based on level
    sequences = COLLEGE_SEQUENCES if level == "college" else HS_SEQUENCES
    position = "neutral"
    # skips iteration the last value because we check the next
    for i, score in enumerate(time_series[:-1]):
        # current time can't be larger than next time
        if time_series[i].time_stamp > time_series[i + 1].time_stamp:
            raise ValueError(
                f"Values in `time_series` appear to be sorted incorrectly."
            )
        if position == "neutral":
            check_neutral(score, sequences['neutral'])
            if score.formatted_label == "fT2" or score.formatted_label == "oBOT":
                position = "top"
            elif score.formatted_label == "oT2" or score.formatted_label == "fBOT":
                position = "bottom"
        elif position == "top":
            check_top(score, sequences['top'])
            if score.formatted_label == "oE1" or score.formatted_label == "fNEU" or score.formatted_label == "oNEU":
                position = "neutral"
            elif score.formatted_label == "oR2" or score.formatted_label == "fBOT" or score.formatted_label == "oTOP":
                position = "bottom"
        elif position == "bottom":
            check_bottom(score, sequences['bottom'])
            if score.formatted_label == "fE1" or score.formatted_label == "fNEU" or score.formatted_label == "oNEU":
                position = "neutral"
            elif score.formatted_label == "fR2" or score.formatted_label == "oBOT" or score.formatted_label == "fTOP":
                position = "top"
        else:
            raise ValueError(
                f"Invalid `position`, expected one of ['neutral', "
                f"'top', 'bottom'], got {position!r}."
            )
    return True
