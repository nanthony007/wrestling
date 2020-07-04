import structures
import pickle
from tqdm import tqdm

with open("college/matches.p", "rb") as f:
    matches = pickle.load(f)

match_list = []
for i, team_matches in enumerate(matches):
    print(i)
    for match in tqdm(team_matches):
        match_list.append(
            structures.CollegeMatch(
                match["matchIDHash"],
                match["matchID"],
                match["eventID"],
                match["theDate"],
                match["timestamp"],
                match["theWeightClass"],  # if type coerced errors like
                # 'Barbee, James'
                match["scoringEvents"],
                int(match["winner"]),
                match["theResult"],
                int(match["teamPoints"]),
                match["redWrestler"],
                match["greenWrestler"],
            )
        )


# for x in dir(m):
#    if x.startswith('opp_') and x not in ['focus_color', 'focus_name',
#                                            'focus_team']:
#       print(x)
