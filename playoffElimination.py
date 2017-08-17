import pandas as pd
from pprint import pprint as pprint

scores_data = pd.read_excel("Analytics_Attachment.xlsx", "2016_17_NBA_Scores")
#print(data)

conferences = {"East":{"all_teams":set()}, "West":{"all_teams":set()}}
conference_data = pd.read_excel("Analytics_Attachment.xlsx", "Division_Info")#.set_index("Conference_id")
for index, data in conference_data.iterrows():
    conference = data["Conference_id"]
    team = data["Team_Name"]
    division = data["Division_id"]
    if division not in conferences[conference]:
        conferences[conference][division] = set([team])
    else:
        conferences[conference][division].add(team)
    conferences[conference]["all_teams"].add(team)
#pprint(conferences)

team_wins = {}
for index, game in scores_data.iterrows():
    date = game["Date"]
    #print(date)
    home = game["Home Team"]
    away = game["Away Team"]
    winner = game["Winner"]
    if winner == "Home":
        if home not in team_wins:
            team_wins[home] = {1:date,away:1}
        else:
            wins = len(team_wins[home]) + 1
            team_wins[home][wins] = date
            if away not in team_wins[home]
    else:
        if away not in team_wins:
            team_wins[away] = {1:date}
        else:
            wins = len(team_wins[away]) + 1
            team_wins[away][wins] = date
#pprint(team_wins)

playoff_team_wins = {"East":[],"West":[]}
for conference in conferences:
    for team in conferences[conference]["all_teams"]:
        wins = len(team_wins[team])
        if len(playoff_team_wins[conference]) < 8:
            playoff_team_wins[conference].append((team,wins))
            playoff_team_wins[conference].sort(key=lambda x: x[1], reverse=True)
        else:
            for index in range(8):
                playoff_team = playoff_team_wins[conference][index][0]
                p_wins = playoff_team_wins[conference][index][1]
                #print(p_wins)
                if wins = p_wins:

                elif wins > p_wins:
                    playoff_team_wins[conference].insert(index,(team,wins))
                    playoff_team_wins[conference].pop()
                    break

playoff_teams = {"East":set(),"West":set()}
for conference in playoff_team_wins:
    for team,wins in playoff_team_wins[conference]:
        playoff_teams[conference].add(team)
pprint(playoff_team_wins)
pprint(playoff_teams)
#
print(conferences["East"]["all_teams"].difference(playoff_teams["East"]))
non_playoff_teams = set()
#for conference in playoff_teams:
#     playoff_teams[conference])
#     print(x[0][0] for x in playoff_teams[conference])
# #     #non_playoff_teams.add(conference[conference]["all_teams"]-set([x[0] for x in playoff_teams[conference]]))
# # #pprint(non_playoff_teams)
