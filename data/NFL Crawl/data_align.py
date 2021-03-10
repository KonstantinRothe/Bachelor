import json
import os.path
import glob
import re
import random
from nltk.tokenize import word_tokenize

teams = [{'franchise': 'Arizona Cardinals', 'abbreviation': 'ARI', 'alt': 'Cardinals', 'city': 'Glendale'},#
                {'franchise': 'Atlanta Falcons', 'abbreviation': 'ATL', 'alt': 'Falcons', 'city': 'Atlanta'},#
                {'franchise': 'Baltimore Ravens', 'abbreviation': 'BAL', 'alt': 'Ravens', 'city': 'Baltimore'},#
                {'franchise': 'Buffalo Bills', 'abbreviation': 'BUF', 'alt': 'Bills', 'city': 'Orchard Park'},#
                {'franchise': 'Carolina Panthers', 'abbreviation': 'CAR', 'alt': 'Panthers', 'city': 'Charlotte'},#
                {'franchise': 'Chicago Bears', 'abbreviation': 'CHI', 'alt': 'Bears', 'city': 'Chicago'},#
                {'franchise': 'Cincinnati Bengals', 'abbreviation': 'CIN', 'alt': 'Bengals', 'city': 'Cincinnati'},#
                {'franchise': 'Cleveland Browns', 'abbreviation': 'CLE', 'alt': 'Browns', 'city': 'Cleveland'},#
                {'franchise': 'Dallas Cowboys', 'abbreviation': 'DAL', 'alt': 'Cowboys', 'city': 'Arlington'},#
                {'franchise': 'Denver Broncos', 'abbreviation': 'DEN', 'alt': 'Broncos', 'city': 'Denver'},#
                {'franchise': 'Detroit Lions', 'abbreviation': 'DET', 'alt': 'Lions', 'city': 'Detroit'},#
                {'franchise': 'Green Bay Packers', 'abbreviation': 'GNB', 'alt': 'Packers', 'city': 'Green Bay'},#
                {'franchise': 'Houston Texans', 'abbreviation': 'HOU', 'alt': 'Texans', 'city': 'Houston'},#
                {'franchise': 'Indianapolis Colts', 'abbreviation': 'IND', 'alt': 'Colts', 'city': 'Indianapolis'},#
                {'franchise': 'Jacksonville Jaguars', 'abbreviation': 'JAX', 'alt': 'Jaguars', 'city': 'Jacksonville'},#
                {'franchise': 'Kansas City Chiefs', 'abbreviation': 'KAN', 'alt': 'Chiefs', 'city': 'Kansas City'},#
                {'franchise': 'Los Angeles Chargers', 'abbreviation': 'LAC', 'alt': 'Chargers', 'city': 'Carson'},#
                {'franchise': 'San Diego Chargers', 'abbreviation': 'SDG', 'alt': 'Chargers', 'city': 'Carson'},#
                {'franchise': 'Los Angeles Rams', 'abbreviation': 'LAR', 'alt': 'Rams', 'city': 'Los Angeles'},#
                {'franchise': 'St. Louis Rams', 'abbreviation': 'STL', 'alt': 'Rams', 'city': 'St. Louis'},#
                {'franchise': 'Las Vegas Raiders', 'abbreviation': 'OAK', 'alt': 'Raiders', 'city': 'Oakland'},#
                {'franchise': 'Miami Dolphins', 'abbreviation': 'MIA', 'alt': 'Dolphins', 'city': 'Miami Gardens'},#
                {'franchise': 'Minnesota Vikings', 'abbreviation': 'MIN', 'alt': 'Vikings', 'city': 'Minneapolis'},#
                {'franchise': 'New England Patriots', 'abbreviation': 'NWE', 'alt': 'Patriots', 'city': 'Foxborough'},#
                {'franchise': 'New Orleans Saints', 'abbreviation': 'NOR', 'alt': 'Saints', 'city': 'New Orleans'},#
                {'franchise': 'New York Giants', 'abbreviation': 'NYG', 'alt': 'Giants', 'city': 'East Rutherford'},#
                {'franchise': 'New York Jets', 'abbreviation': 'NYJ', 'alt': 'Jets', 'city': 'East Rutherford'},#
                {'franchise': 'Philadelphia Eagles', 'abbreviation': 'PHI', 'alt': 'Eagles', 'city': 'Philadelphia'},#
                {'franchise': 'Pittsburgh Steelers', 'abbreviation': 'PIT', 'alt': 'Steelers', 'city': 'Pittsburgh'},#
                {'franchise': 'Seattle Seahawks', 'abbreviation': 'SEA', 'alt': 'Seahawks', 'city': 'Seattle'},#
                {'franchise': 'San Francisco 49ers', 'abbreviation': 'SFO', 'alt': '49ers', 'city': 'Santa Clara'},#
                {'franchise': 'Tampa Bay Buccaneers', 'abbreviation': 'TAM', 'alt': 'Buccaneers', 'city': 'Tampa'},#
                {'franchise': 'Tennessee Titans', 'abbreviation': 'TEN', 'alt': 'Titans', 'city': 'Nashville'},#
                {'franchise': 'Washington Football Team', 'abbreviation': 'WAS', 'alt': 'Redskins', 'city': 'Landover'}]#

def splitData():
    print("Splitting data...")
    json_data = open('nfl dataset\\games.json')
    data = json.load(json_data)
    for playerdata in data:
        if(2008 <= int(playerdata['year'])):
            vis_name = playerdata['opponent']
            vis_score = playerdata['opponent_score']
            home_name = playerdata['team']
            home_score = playerdata['player_team_score']
            #swap the opponent and home teams if it wasnt a home game
            if(playerdata['game_location'] != 'H'):
                vis_name = playerdata['team']
                vis_score = playerdata['player_team_score']
                home_name = playerdata['opponent']
                home_score = playerdata['opponent_score']

            year = playerdata['year']
            filename = 'gamedata\\{} {} {}-{} {}.json'.format(year, vis_name, vis_score, home_name, home_score)
            #create a new file with the content of each playerdata for a specific game
            if(not os.path.isfile(filename)):
                file = open(filename, 'w')
                file.write(str(playerdata))
                file.close()
            else:
                file = open(filename, 'a')#
                file.write(str(playerdata))
                file.close()
    print("Done splitting data!")

def toListOfJSON():
    #this regex ensures that every non-string value gets encapsulated in double quotation marks
    reg = r"(?<=:\s)[^\"].*?(?=[,^}])"
    print("Formatting to JSON...")
    for file in glob.glob("gamedata\\"+"*.json"):
        f = open(file, 'r')
        data = f.read()
        _f = re.sub(r'^{.*}$', '[\\g<0>]', data)
        _f = re.sub('}{', '},{',_f)
        _f = re.sub("\'", '\"', _f)
        _f = re.sub(reg, "\"\\g<0>\"", _f)
        #override old file with new content
        g = open(file, 'w')
        g.write(_f)
        g.close()
        f.close()
        print("Done making a list out of file {}".format(file))
    print("Done formatting!")

def getPlayerInfo(files = '*'):
    playerfile = open("nfl dataset\\playerprofiles.json")
    playerdata = json.load(playerfile)
    if(files):
        _f = files

    for file in glob.glob("gamedata\\"+"{}.json".format(_f)):
        with open(file, 'r+') as json_data:
            data = json.load(json_data)
            for stat in data:
                name = ''
                position = ''
                for player in playerdata:
                    if(str(player['player_id']) == stat['player_id']):
                        name = player['name']
                        position = player['position']
                        break
                new_entry = {"name": "{}".format(name), "position": "{}".format(position)}
                stat.update(new_entry)
            json_data.seek(0)
            json.dump(data, json_data)
        print("Done extracting data for file {}!".format(file))
    playerfile.close()
    print("Done extracting all data!")
        
def formatGameData(allfiles = False):
    if(allfiles):
        _f = allfiles
    else:
        _f = "*"
    counter = 0
    summaries = 0
    for file in glob.glob("gamedata\\"+"{}.json".format(_f)):  
        with open(file, "r") as unformatted:
            raw_data = json.load(unformatted)
            home_total_plays = 0
            home_passing_yards = 0 #sum of passing yards - yards lost to sacks
            home_rushing_yards = 0
            home_total_yards = 0
            idcounter = 0

            pseudo_home = ''

            game_json = {
                'home_name': '',
                'home_city': '',
                'vis_name': '',
                'vis_city': '',
                'day': '',
                'summary': [],
                'box_score': {
                    'FIRST_NAME': {},
                    'SECOND_NAME': {},
                    'PLAYER_NAME': {},
                    'TEAM': {},
                    'POSITION': {},
                    'PASSING_ATTEMTPS': {},
                    'PASSING_COMPLETIONS': {},
        	        'PASSING_YARDS': {},
        		    'PASSING_TOUCHDOWNS': {},
        			'PASSING_INTERCEPTIONS': {},
        			'PASSING_SACKS': {},
        			'PASSING__SACKS_YARDS_LOST': {},
        			'PASSING_RATE': {},
                    #RUSHING
        			'RUSHING_ATTEMPTS': {},
        			'RUSHING_YARDS': {},
        			'RUSHING_TOUCHDOWNS': {},
                    #RECEIVING
        			'RECEIVING_RECEPTIONS': {},
        			'RECEIVING_YARDS': {},
        			'RECEIVING_TOUCHDOWNS': {},
                    'RECEIVING_TARGETS': {},
                    #DEFENSIVE INTERCEPTIONS
        			'INTERCEPTION_PASSING': {},
        			'INTERCEPTION_YARDS': {},
        			'INTERCEPTION_TOUCHDOWNS': {},
                    #SACKS
        			'SACKS': {},
                    #TACKLES
        			'TACKLES_COMBINED': {}, # solo + assists
        			'TACKLES_SOLO': {},
        			'TACKLES_ASSISTS': {},
                    #KICK RETURNS
        			'KICK_ATTEMPTS': {},
        			'KICK_YARDS': {},
        			'KICK_TOUCHDOWNS': {},
                    #PUNT RETURNS
        			'PUNT_ATTEMPTS': {},
        			'PUNT_YARDS': {},
        			'PUNT_AVERAGE': {},
                    'PUNT_TOUCHDOWNS': {}
                },
                'vis_line': {
                    'TEAM_PTS': "",
                    'TEAM_CITY': "",
                    'TEAM_NAME': ""
                },
                'home_line': {
                    'TEAM_PTS': "",
                    'TEAM_CITY': "",
                    'TEAM_NAME': ""
                },
            }  
            
            lineScore =  {
                'home': {
                    'TEAM_PTS': "",
                    'TEAM_CITY': "",
                    'TEAM_NAME': "",
                    'TOTAL_PLAYS': 1,
                    'TOTAL_YARDS': 0,
                    'YARDS_PER_PLAY': 0,
                    'PASSING_YARDS': 0,
                    'RUSHING_YARDS': 0,
                    'DEFENSIVE_SPECIAL_TOUCHDOWNS': 0
                },
                'vis': {
                    'TEAM_PTS': "",
                    'TEAM_CITY': "",
                    'TEAM_NAME': "",
                    'TOTAL_PLAYS': 1,
                    'TOTAL_YARDS': 0,
                    'YARDS_PER_PLAY': 0,
                    'PASSING_YARDS': 0,
                    'RUSHING_YARDS': 0,
                    'DEFENSIVE_SPECIAL_TOUCHDOWNS': 0
                }
            }

            for stat in raw_data:
                if(stat['game_location'] == "H"):
                    side = 'home'
                elif(stat['game_location'] == "A"):
                    side = 'vis'
                else: #game_location == 'N' -> entscheiden, welches team als home und welches als vis spielt --> funktioniert nicht!
                   break

                if(game_json['day'] == ''):
                    date = stat['date'].split("-")
                    year = date[0][2:]
                    month = date[1]
                    day = date[2]
                    game_json['day'] = "{}_{}_{}".format(month, day, year)
                
                #line score collection
                lineScore[side]['TOTAL_PLAYS'] += int(stat['passing_attempts']) + int(stat['rushing_attempts'])
                lineScore[side]['PASSING_YARDS'] += int(stat['passing_yards'])
                lineScore[side]['RUSHING_YARDS'] += int(stat['rushing_yards'])
                lineScore[side]['TOTAL_YARDS'] += int(lineScore[side]['PASSING_YARDS']) + int(lineScore[side]['RUSHING_YARDS'])
                if(int(lineScore[side]['TOTAL_PLAYS']) > 0):
                    lineScore[side]['YARDS_PER_PLAY'] = float(lineScore[side]['TOTAL_YARDS']) / float(lineScore[side]['TOTAL_PLAYS'])
                lineScore[side]['DEFENSIVE_SPECIAL_TOUCHDOWNS'] += int(stat['defense_interception_touchdowns']) + int(stat['punt_return_touchdowns']) + int(stat['kick_return_touchdowns'])

                if(lineScore[side]['TEAM_PTS'] == ""):
                    lineScore[side]['TEAM_PTS'] = stat['player_team_score']


                playerteam = ''

                for team in teams:
                    if(stat['team'] == team['abbreviation']):
                        playerteam = team['city']
                        #check if home_name, .. are already set to not override it each time
                        game_json[side+'_name'] = team['alt']
                        game_json[side+'_city'] = team['city']
                        if(lineScore[side]['TEAM_CITY'] == ""):
                            lineScore[side]['TEAM_CITY'] = team['city']
                        if(lineScore[side]['TEAM_NAME'] == ""):
                            lineScore[side]['TEAM_NAME'] = team['franchise']

                #box score 
                playername = stat['name']
                playerid = idcounter #stat['player_id']

                game_json['box_score']['PLAYER_NAME'][playerid] = playername
                game_json['box_score']['FIRST_NAME'][playerid] = playername.split()[0]
                secondname = ''
                for snames in playername.split()[1:]:
                    secondname += "{} ".format(snames)
                secondname.rstrip()
                game_json['box_score']['SECOND_NAME'][playerid] = secondname
                game_json['box_score']['TEAM'][playerid] = playerteam
                game_json['box_score']['POSITION'][playerid] = stat['position']
                #PASSING
                game_json['box_score']['PASSING_ATTEMTPS'][playerid] = stat['passing_attempts']
                game_json['box_score']['PASSING_COMPLETIONS'][playerid] = stat['passing_completions']
                game_json['box_score']['PASSING_YARDS'][playerid] = stat['passing_yards']
                game_json['box_score']['PASSING_TOUCHDOWNS'][playerid] = stat['passing_touchdowns']
                game_json['box_score']['PASSING_INTERCEPTIONS'][playerid] = stat['passing_interceptions']
                game_json['box_score']['PASSING_SACKS'][playerid] = stat['passing_sacks']
                game_json['box_score']['PASSING__SACKS_YARDS_LOST'][playerid] = stat['passing_sacks_yards_lost']
                game_json['box_score']['PASSING_RATE'][playerid] = stat['passing_rating']
                #RUSHING
                game_json['box_score']['RUSHING_ATTEMPTS'][playerid] = stat['rushing_attempts']
                game_json['box_score']['RUSHING_YARDS'][playerid] = stat['rushing_yards']
                game_json['box_score']['RUSHING_TOUCHDOWNS'][playerid] = stat['rushing_touchdowns']
                #RECEIVING
                game_json['box_score']['RECEIVING_RECEPTIONS'][playerid] = stat['receiving_receptions']
                game_json['box_score']['RECEIVING_YARDS'][playerid] = stat['receiving_yards']
                game_json['box_score']['RECEIVING_TOUCHDOWNS'][playerid] = stat['receiving_touchdowns']
                game_json['box_score']['RECEIVING_TARGETS'][playerid] = stat['receiving_targets']
                #DEFENSIVE INTERCEPTIONS
                game_json['box_score']['INTERCEPTION_PASSING'][playerid] = stat['defense_interceptions']
                game_json['box_score']['INTERCEPTION_YARDS'][playerid] = stat['defense_interception_yards']
                game_json['box_score']['INTERCEPTION_TOUCHDOWNS'][playerid] = stat['defense_interception_touchdowns']
                #SACKS
                game_json['box_score']['SACKS'][playerid] = stat['defense_sacks']
                #TACKLES
                tackles_combined = int(stat['defense_tackles']) + int(stat['defense_tackle_assists'])
                game_json['box_score']['TACKLES_COMBINED'][playerid] = str(tackles_combined) # solo + assists
                game_json['box_score']['TACKLES_SOLO'][playerid] = stat['defense_tackles']
                game_json['box_score']['TACKLES_ASSISTS'][playerid] = stat['defense_tackle_assists']
                #KICK RETURNS
                game_json['box_score']['KICK_ATTEMPTS'][playerid] = stat['kick_return_attempts']
                game_json['box_score']['KICK_YARDS'][playerid] = stat['kick_return_yards']
                game_json['box_score']['KICK_TOUCHDOWNS'][playerid] = stat['kick_return_touchdowns']
                #PUNT RETURNS
                if(float(stat['punt_return_attempts']) != 0):
                    punt_average = str(float(stat['punt_return_yards']) / float(stat['punt_return_attempts']))
                else:
                    punt_average = "0.0"
                game_json['box_score']['PUNT_ATTEMPTS'][playerid] = stat['punt_return_attempts']
                game_json['box_score']['PUNT_YARDS'][playerid] = stat['punt_return_yards']
                game_json['box_score']['PUNT_AVERAGE'][playerid] = punt_average
                game_json['box_score']['PUNT_TOUCHDOWNS'][playerid] = stat['punt_return_touchdowns']
            
                idcounter += 1

            #convert numerical values to string
            h_keys_values = lineScore['home'].items()
            _home_line = {str(key): str(value) for key, value in h_keys_values}

            v_keys_values = lineScore['vis'].items()
            _vis_line = {str(key): str(value) for key, value in v_keys_values}

            game_json['home_line'] = _home_line
            game_json['vis_line'] = _vis_line

            #finally, find right summary and add it to the file
            filename = "{} {}-{} {} {}".format(game_json['home_name'], game_json['home_line']['TEAM_PTS'], game_json['vis_name'], game_json['vis_line']['TEAM_PTS'], game_json['day'])
        
            summary = getReviewAsTokens(game_json['home_name'], game_json['home_line']['TEAM_PTS'], game_json['vis_name'], game_json['vis_line']['TEAM_PTS'], game_json['day'][-2:])

            if(not summary):
                summary = getReviewAsTokens(game_json['vis_name'], game_json['vis_line']['TEAM_PTS'], game_json['home_name'], game_json['home_line']['TEAM_PTS'], game_json['day'][-2:])

            if(summary):
                summaries += 1
            else:
                print("Couldn't find summary for game {}".format(filename))
                  

            game_json['summary'] = summary
            counter += 1
            writeJSON(game_json, "finalData\\{}.json".format(filename))
            
            print("Wrote to file {}.json".format(filename))
    print("Formatted {} files, {} of them have a summary.".format(counter, summaries))

def getReviewAsTokens(home, homescore, vis, visscore, year):
    filestring = "{} {}-{} {}_20{}".format(home, homescore, vis, visscore, year)
    #print(filestring)
    for file in glob.glob("reviews\\{}".format(filestring)+"*.txt"):
        with open(file) as f:
            data = f.read()
            if(data):
                return word_tokenize(data)
            else:
                return []

def removeGamesWithoutSummary():
    counter = 0
    for file in glob.glob("finalData\\" + "*.json"):
        json_data = open(file, "r")
        ignoreflag = False
        print("Checking file {}...".format(file))
        data = json.load(json_data)
        try:
            if(data['summary'] is None):
                print("No summary")
                counter += 1
                ignoreflag = True
        except KeyError:
            print("KeyError for file {}".format(file))
            if(not 'summary' in data):
                counter += 1
                ignoreflag = True
        finally:
            json_data.close()
            if(ignoreflag):
                os.rename(file, "{}.ignore".format(file))
    print("Ignoring {} files".format(counter))

def undoRename():
    for file in glob.glob("finalData\\"+"*.ignore"):
        os.rename(file, file[0:-len(".ignore")])
        #print(file[0:-len(".ignore")])

def createFinalData(trainingperc = 0.7):
    assert 0 < trainingperc > 1

    validperc = (1-trainingperc) / 2
    testperc = validperc
    train = []
    test = []
    valid = []
    biglist = []
    for file in glob.glob("finalData\\" + "*.json"):
        with open(file) as f:
            json_data = json.load(f)
            biglist.append(json_data)
            validperc = (1-trainingperc) / 2
            testperc = validperc
            z = random.uniform(0, 1)
            #print(z) 
            if(0 <= z <= trainingperc): #z in [0..0.7]
                train.append(json_data)
            elif(trainingperc < z <= trainingperc+testperc): #z in )0.7..0.85]
                test.append(json_data)
            elif(trainingperc+testperc < z <= 1): #z in )0.85..1]
                valid.append(json_data)
            else:
                print("Something went terribly wrong")

    random.shuffle(biglist) #this is used to create a source dictionary
    writeJSON(biglist, "transformer_input\\biglist.json")

    random.shuffle(train)
    for i in train:
        remove = random.uniform(0,1)
        if(remove <= .5):
            train.remove(i)
    writeJSON(train, "transformer_input\\train.json")

    random.shuffle(test)
    for i in test:
        remove = random.uniform(0,1)
        if(remove <= .5):
            test.remove(i)
    writeJSON(test, "transformer_input\\test.json")

    random.shuffle(valid)
    for i in valid:
        remove = random.uniform(0,1)
        if(remove <= .5):
            valid.remove(i)
    writeJSON(valid, "transformer_input\\valid.json")
    # print("Train: {}".format(train))
    # print("\n --------------------- \n")
    # print("Test: {}".format(test))
    # print("\n --------------------- \n")
    # print("Valid: {}".format(valid))


def writeJSON(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f)
    print("Wrote data to {}".format(filename))

#splitData()
#toListOfJSON()
#getPlayerInfo()
#formatGameData()
#removeGamesWithoutSummary()
#createFinalData()