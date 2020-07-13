# this module contains the dicts for valid sequence of events

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
