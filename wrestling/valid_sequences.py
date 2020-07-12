# this module contains the dicts for valid sequence of events

_college_always = [
    'fBOT', 'fTOP', 'fNEU', 'fDEFER',
    'oBOT', 'oTOP', 'oNEU', 'oDEFER',
    'fC', 'fP1', 'fP2', 'fWS', 'fS1', 'fS2',
    'oC', 'oP1', 'oP2', 'oWS', 'oS1', 'oS2',
    'fRO1', 'oRO1',
]
_college_focus_top = ['fN2', 'fN4', 'oE1', 'oR2']
_college_focus_bottom = ['oN2', 'oN4', 'fE1', 'fR2']
_college_neutral = ['fT2', 'oT2']

college_sequences = dict(
    fT2=set(_college_focus_top + _college_always),
    oT2=set(_college_focus_bottom + _college_always),
    fE1=set(_college_neutral + _college_always),
    oE1=set(_college_neutral + _college_always),
    fR2=set(_college_focus_top + _college_always),
    oR2=set(_college_focus_bottom + _college_always),
    fN2=set(_college_focus_top + _college_always),
    oN2=set(_college_focus_bottom + _college_always),
    fN4=set(_college_focus_top + _college_always),
    oN4=set(_college_focus_bottom + _college_always),
)

_hs_always = [
    'fBOT', 'fTOP', 'fNEU', 'fDEFER',
    'oBOT', 'oTOP', 'oNEU', 'oDEFER',
    'fC', 'fP1', 'fP2', 'fWS', 'fS1', 'fS2',
    'oC', 'oP1', 'oP2', 'oWS', 'oS1', 'oS2',
]
_hs_focus_top = ['fN2', 'fN3', 'oE1', 'oR2']
_hs_focus_bottom = ['oN2', 'oN3', 'fE1', 'fR2']
_hs_neutral = ['fT2', 'oT2']

hs_sequences = dict(
    fT2=set(_hs_focus_top + _hs_always),
    oT2=set(_hs_focus_bottom + _hs_always),
    fE1=set(_hs_neutral + _hs_always),
    oE1=set(_hs_neutral + _hs_always),
    fR2=set(_hs_focus_top + _hs_always),
    oR2=set(_hs_focus_bottom + _hs_always),
    fN2=set(_hs_focus_top + _hs_always),
    oN2=set(_hs_focus_bottom + _hs_always),
    fN4=set(_hs_focus_top + _hs_always),
    oN4=set(_hs_focus_bottom + _hs_always),
)
