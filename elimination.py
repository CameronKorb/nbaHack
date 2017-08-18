import pandas as pd

import config


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


def get_possible_wins_naive(data):
    data['Max Possible Wins'] = data['Total Wins'] + data['Games Left']
    data['Eliminated'] = data['Max Possible Wins'] < data['Wins To Beat']

    return data


def get_elimination_dates(teams, data):
    data = data.drop_duplicates(subset=['Team_Name', 'Eliminated'])
    data = data.drop_duplicates(subset=['Team_Name'], keep='last')
    data.loc[data['Eliminated'], 'Elimination Date'] = data['Date']
    data['Elimination Date'] = data['Elimination Date'].fillna('Playoffs')

    data = data[['Team_Name', 'Elimination Date']]

    data.to_csv('output/elimination_dates.csv')

    return data


def main():
    scores_df = get_season_scores()
    teams_df = get_team_info()
    df = compute_wins(scores_df, teams_df)
    df = compute_games_left(df, scores_df, teams_df)
    df = get_minimum_top_8_wins(df)
    df = get_possible_wins_naive(df)
    get_elimination_dates(teams_df, df)
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