
import re
from collections import Counter, namedtuple
from datetime import datetime
from typing import List, Tuple, Optional, Dict
from uuid import uuid4
import urllib


# this is similar to the parse function in jupyter
# could use that then this to create the events
def generate_time_series(obj, actions, toggle):
	scoring_events = (
		[HighSchoolScoringEvent(focus=obj.focus_color)]
		if toggle == "high_school"
		else [CollegeScoringEvent(focus=obj.focus_color)]
	)
	if len(actions) == 0:
		return scoring_events
	for action in actions.split("#"):
		if action == "****" or action.split("*")[0] == "NaN":
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
			HighSchoolScoringEvent(focus=obj.focus_color, **action_dict)
			if toggle == "high_school"
			else CollegeScoringEvent(focus=obj.focus_color, **action_dict)
		)
		scoring_events.append(new_event)
	return scoring_events
