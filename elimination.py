import pandas as pd
from pprint import pprint as pprint
import config
import numpy as np
from datetime import date as date

# TODO: change so instead of passing dfs, it's using pickle files


def get_season_scores():
    scores = pd.read_csv('input/scores.csv')
    scores['Date'] = pd.to_datetime(scores['Date'], format="%m/%d/%y")

    return scores


def get_team_info():
    teams = pd.read_csv('input/teams.csv')

    return teams


def cross_teams_dates(scores, teams):
    dates = pd.DataFrame(data=scores['Date'].drop_duplicates())

    # keys for cross product merging purposes
    dates['key'] = 1
    teams['key'] = 1

    # gets a list where team name and all the dates that there were nba games
    df = teams.merge(dates, on='key', how='outer').drop('key', axis=1)

    return df


def compute_wins(scores, teams):
    df = cross_teams_dates(scores, teams)

    # first get home wins
    df = df.merge(scores, left_on=['Team_Name', 'Date'], right_on=['Home Team', 'Date'], how='outer').\
        drop('Home Team', axis=1)
    df.loc[df['Winner'] == 'Home', 'Win'] = 1.
    df = df.rename(columns={'Away Team': 'Team Played'})
    df = df.drop(['Home Score', 'Away Score', 'Winner'], axis=1)

    # get away wins
    df = df.merge(scores, left_on=['Team_Name', 'Date'], right_on=['Away Team', 'Date'], how='outer').\
        drop('Away Team', axis=1)
    df.loc[df['Winner'] == 'Away', 'Win'] = 1.
    df.loc[df['Team Played'].isnull(), 'Team Played'] = df['Home Team']
    df = df.drop(['Home Team', 'Home Score', 'Away Score', 'Winner'], axis=1)

    # drop dates when the team did not play, fill in losses
    df = df.dropna(subset=['Team Played'])
    df.loc[df['Win'].isnull(), 'Win'] = 0.

    # get cumulative sum of wins by date, where 'Total Wins' represents number of wins
    # up to and including that game
    df =  df.sort_values(by=['Team_Name', 'Date'], ascending=[1, 1])
    df['Total Wins'] = df.groupby('Team_Name')['Win'].cumsum()

    df = df.reset_index().drop('index', axis=1)

    df.to_csv('output/total_wins.csv')

    return df

def compute_results_teamwise(data, scores, teams):
    data['Games Against'] = data.groupby(['Team_Name', 'Team Played']).cumcount() + 1
    data['Wins Against'] = data.groupby(['Team_Name', 'Team Played'])['Win'].cumsum()

    data = data.sort_values(by=['Team_Name', 'Date'], ascending=[1, 1]).reset_index().drop('index', axis=1)
    data = data.drop_duplicates(subset=['Team_Name', 'Team Played'], keep='last')

    data = data[['Team_Name', 'Team Played', 'Games Against', 'Wins Against']]

    return data

def compute_games_left(data, scores, teams):
    data['Games Played'] = data.groupby('Team_Name').cumcount() + 1
    data['Games Left'] = config.NUM_GAMES - data['Games Played']

    df = cross_teams_dates(scores, teams)
    df = df.merge(data, on=['Team_Name', 'Division_id', 'Conference_id', 'Date'], how='outer')

    df[['Total Wins', 'Games Played', 'Games Left']] = \
        df.groupby('Team_Name')[['Total Wins', 'Games Played', 'Games Left']].fillna(method='ffill')

    return df


def get_minimum_top_8_wins(data):
    min_score = data.groupby(['Date', 'Conference_id'], as_index=False).\
        apply(lambda group: group['Total Wins'].nlargest(8).min())

    min_score_df = pd.DataFrame(data=min_score).reset_index()
    min_score_df.columns = ['Date', 'Conference_id', 'Wins To Beat']

    data = data.merge(min_score_df, on=['Date', 'Conference_id'])
    data =  data.sort_values(by=['Team_Name', 'Date'], ascending=[1, 1]).reset_index().drop('index', axis=1)

    return data




def get_possible_wins(data):
    data['Max Possible Wins'] = data['Total Wins'] + data['Games Left']
    data['Eliminated'] = 'Playoffs'
    data.loc[data['Max Possible Wins'] < data['Wins To Beat'], 'Eliminated'] = 'yes'
    data.loc[data['Max Possible Wins'] == data['Wins To Beat'], 'Eliminated'] = 'tie'

    return data

def tie_breaker(teams, results_teamwise):
    #8th place team makes it automatically
    if len(teams) == 1:
        return teams.get_value(0,'Team_Name')

    #2 way tie for 8th place, head to head wins is first tie breaker, don't need more for 2016/2017
    if len(teams) == 2:
        result = results_teamwise.loc[(results_teamwise['Team_Name'] == teams.iloc[0]['Team_Name']) & \
                                    (results_teamwise['Team Played'] == teams.iloc[1]['Team_Name'])].reset_index()
        if result.get_value(0,'Wins Against')/ result.get_value(0,'Games Against') > .5:
            return result.get_value(0,'Team_Name')
        elif result.get_value(0,'Wins Against')/ result.get_value(0,'Games Against') < .5:
            return result.get_value(0,'Team Played')
        else:
            #Go to next tie breaker rule...
            pass

    #3 way tie for 7th/8th place, division leader is first tie breaker
    #didn't happen in 2016/2017
    if len(teams) == 3:
        pass


def get_elimination_dates(teams, data, results_teamwise):
    data = data.drop_duplicates(subset=['Team_Name', 'Eliminated'])

    data = data.drop_duplicates(subset=['Team_Name'], keep='last')
    data.loc[data['Eliminated'] == 'yes', 'Elimination Date'] = data['Date']
    data.loc[data['Eliminated'] == 'tie', 'Elimination Date'] = data['Date']
    data['Elimination Date'] = data['Elimination Date'].fillna('Playoffs')


    east_ties = data.loc[(data['Eliminated'] == 'tie') & (data["Conference_id"] == 'East')][['Team_Name']].reset_index()
    west_ties = data.loc[(data['Eliminated'] == 'tie') & (data["Conference_id"] == 'West')][['Team_Name']].reset_index()
    east_tie_win = tie_breaker(east_ties, results_teamwise)
    west_tie_win = tie_breaker(west_ties, results_teamwise)

    data.loc[(data['Eliminated'] == 'tie') & (data['Conference_id'] == 'East') \
                    & (data['Team_Name'] == east_tie_win), 'Elimination Date'] = 'Playoffs'
    data.loc[(data['Eliminated'] == 'tie') & (data['Conference_id'] == 'West') \
                    & (data['Team_Name'] == west_tie_win), 'Elimination Date'] = 'Playoffs'


    data = data[['Team_Name', 'Elimination Date']]
    data.columns = ['Team', 'Date Eliminated']
    data['Date Eliminated'].apply(lambda x: str(date.fromordinal(x.toordinal())) if x != 'Playoffs' else x)
    data = data.set_index('Team')
    pprint(data)

    writer = pd.ExcelWriter('output/elimination_dates.xlsx',
                        engine='xlsxwriter',
                        datetime_format='mm/dd/yyyy',
                        date_format='mmm/dd/yyyy')
    data.to_excel(writer)

    return data


def main():
    scores_df = get_season_scores()
    teams_df = get_team_info()
    df = compute_wins(scores_df, teams_df)
    results_teamwise = compute_results_teamwise(df, scores_df, teams_df)
    df = compute_games_left(df, scores_df, teams_df)
    df = get_minimum_top_8_wins(df)
    df = get_possible_wins(df)
    get_elimination_dates(teams_df, df, results_teamwise)
    # east_teams = (teams_df[teams_df['Conference_id'] == 'East'], 'east')
    # west_teams = (teams_df[teams_df['Conference_id'] == 'West'], 'west')
    # for conference in [east_teams, west_teams]:
    #     team_df = conference[0]
    #     label = conference[1]
    #     df = compute_wins(scores_df, team_df)
    #     df = compute_games_left(df, scores_df, team_df)
    #     df = get_minimum_top_8_wins(df)
    #     df = get_possible_wins_naive(df)
    #     df = get_elimination_dates(teams_df, df)
    #
    #     df.to_csv('output/elimination_dates_{}.csv'.format(label))


if __name__ == '__main__':
    main()
