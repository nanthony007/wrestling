#! /usr/bin/python

"""Module for determining validity of time_series sequences.

This module checks the time_series attribute of a Match for its conditional
validity based on the position.  It is used in the Match.time_series
validator.  Helper functions for checking the next event in a sequence based
on a given position are also provided.

"""

from typing import Dict, Set, Tuple, Union

from wrestling.scoring import CollegeScoring, HSScoring

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
    "fRT1",
    "oRT1",
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
"""Dictionary of valid college next-moves based on position."""

HS_SEQUENCES = dict(
    neutral=set(_hs_neutral + _always),
    top=set(_hs_focus_top + _always),
    bottom=set(_hs_focus_bottom + _always),
    always=set(_always),
)
"""Dictionary of valid high school next-moves based on position."""


def check_neutral(score: Union[CollegeScoring, HSScoring], seq: Set[str]):
    """Checks if next move is valid in neutral position.

    Args:
        score: Either CollegeScoring or HSScoring instance.
        seq (Dict): HS_SEQUENCES or COLLEGE_SEQUENCES to check the 'score' against.

    """
    if score.formatted_label not in seq:
        # invalid
        score.label.isvalid = False
        score.label.msg = (
            f"Not a valid neutral move, expected one of {*seq,}, "
            f"but got {score.formatted_label}."
        )


def check_top(score: Union[CollegeScoring, HSScoring], seq: Set[str]):
    """Checks if next move is valid in top position.

    Args:
        score: Either CollegeScoring or HSScoring instance.
        seq (Dict): HS_SEQUENCES or COLLEGE_SEQUENCES to check the 'score' against.
    
    """
    if score.formatted_label not in seq:
        # invalid
        score.label.isvalid = False
        score.label.msg = (
            f"Not a valid top move, expected one of {*seq,}, "
            f"but got {score.formatted_label}."
        )


def check_bottom(score: Union[CollegeScoring, HSScoring], seq: Set[str]):
    """Checks if next move is valid in bottom position.

    Args:
        score: Either CollegeScoring or HSScoring instance.
        seq (Dict): HS_SEQUENCES or COLLEGE_SEQUENCES to check the 'score' against.

    """
    if score.formatted_label not in seq:
        # invalid
        score.label.isvalid = False
        score.label.msg = (
            f"Not a valid bottom move, expected one of {*seq,}, "
            f"but got {score.formatted_label}."
        )


def isvalid_sequence(
        level: str, time_series: Tuple[Union[HSScoring, CollegeScoring]]
) -> bool:
    """Checks if entire sequence is valid.

    Args:
        level: 'high school' or 'college' level for sequence analysis.
        time_series: Tuple of sorted match time_series events.

    Raises:
        ValueError: Invalid level.
        ValueError: Not sorted time_series.
        ValueError: Invalid position.

    Returns:
        bool: True if sequence is valid, otherwise raises ValueError.
    """
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
            check_neutral(score, sequences["neutral"])
            if score.formatted_label == "fT2" or score.formatted_label == "oBOT" or score.formatted_label == 'fTOP':
                position = "top"
            elif score.formatted_label == "oT2" or score.formatted_label == "fBOT" or score.formatted_label == 'oTOP':
                position = "bottom"
        elif position == "top":
            check_top(score, sequences["top"])
            if (
                    score.formatted_label == "oE1"
                    or score.formatted_label == "fNEU"
                    or score.formatted_label == "oNEU"
            ):
                position = "neutral"
            elif (
                    score.formatted_label == "oR2"
                    or score.formatted_label == "fBOT"
                    or score.formatted_label == "oTOP"
            ):
                position = "bottom"
        elif position == "bottom":
            check_bottom(score, sequences["bottom"])
            if (
                    score.formatted_label == "fE1"
                    or score.formatted_label == "fNEU"
                    or score.formatted_label == "oNEU"
            ):
                position = "neutral"
            elif (
                    score.formatted_label == "fR2"
                    or score.formatted_label == "oBOT"
                    or score.formatted_label == "fTOP"
            ):
                position = "top"
        else:
            raise ValueError(
                f"Invalid `position`, expected one of ['neutral', "
                f"'top', 'bottom'], got {position!r}."
            )
    return True
