# this module contains the dicts for valid sequence of events

from typing import Tuple

always = [
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

college_sequences = dict(
    neutral=set(_college_neutral + always),
    top=set(_college_focus_top + always),
    bottom=set(_college_focus_bottom + always),
    always=set(always),
)

hs_sequences = dict(
    neutral=set(_hs_neutral + always),
    top=set(_hs_focus_top + always),
    bottom=set(_hs_focus_bottom + always),
    always=set(always),
)


# checks formatted label strings (fT2 or oE1)
# checks value and evaluates list of possible next values
def isvalid_sequence(level: str, time_series: Tuple):
    assert level in {"college", "high school"}, (
        f"Expected `level` to be one of "
        f"'college' or 'high school', "
        f"got {level!r}."
    )
    # aliases sequences based on level
    sequences = college_sequences if level == "college" else hs_sequences
    position = "neutral"
    # skips iteration the last value because we check the next
    for i, score in enumerate(time_series[:-1]):
        assert (
                time_series[i].time_stamp <= time_series[i + 1].time_stamp
        ), f"Values in `time_series` appear to be sorted incorrectly."
        lab = score.formatted_label
        if position == "neutral":
            assert lab in sequences["neutral"], (
                f"Not a valid neutral move, expected one of"
                f" {sequences['neutral']}, but got {lab}."
            )
            if lab == "fT2" or lab == "oBOT":
                position = "top"
            elif lab == "oT2" or lab == "fBOT":
                position = "bottom"
        elif position == "top":
            assert lab in sequences["top"], (
                f"Not a valid neutral move, expected one of"
                f" {sequences['top']}, but got {lab}."
            )
            if lab == "oE1" or lab == "fNEU" or lab == "oNEU":
                position = "neutral"
            elif lab == "oR2" or lab == "fBOT" or lab == "oTOP":
                position = "bottom"
        elif position == "bottom":
            assert lab in sequences["bottom"], (
                f"Not a valid neutral move, expected one of"
                f" {sequences['bottom']}, but got {lab}."
            )
            if lab == "fE1" or lab == "fNEU" or lab == "oNEU":
                position = "neutral"
            elif lab == "fR2" or lab == "oBOT" or lab == "fTOP":
                position = "top"
        else:
            raise ValueError(
                f"Invalid `position`, expected one of ['neutral', "
                f"'top', 'bottom'], got {position!r}."
            )
    return True
