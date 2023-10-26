import requests 
import pandas
import time

api_key = "RGAPI-2a03cb53-8821-40a8-8af3-f1e21079414e"

summoner_name = input("Input summoner name: ")
region = "na1"
mass_region = "AMERICAS"
no_games = 25 
queue_type = input("Input desired queue type (ARAM, Ranked Solo, Ranked Flex, Draft, Blind): ")
if(queue_type == "ARAM"):
    queue_id = 450
elif(queue_type == "Ranked Solo"):
    queue_id = 420
elif(queue_type == "Ranked Flex"):
    queue_id = 440
elif(queue_type == "Draft"):
    queue_id = 400
elif(queue_type == "Blind"):
    queue_id = 430

#Get the puuid, given a summoner name and region
def get_puuid(summoner_name, region, api_key):
    api_url = (
        "https://" + 
        region +
        ".api.riotgames.com/lol/summoner/v4/summoners/by-name/" +
        summoner_name +
        "?api_key=" +
        api_key
    )

    resp = requests.get(api_url)
    player_info = resp.json()
    puuid = player_info['puuid']
    return puuid  

#Get a list of all the match IDs given a players puuid and mass region
def get_match_ids(puuid, mass_region, no_games, queue_id, api_key):
    api_url = (
        "https://" +
        mass_region +
        ".api.riotgames.com/lol/match/v5/matches/by-puuid/" +
        puuid + 
        "/ids?start=0" + 
        "&count=" +
        str(no_games) + 
        "&queue=" + 
        str(queue_id) + 
        "&api_key=" + 
        api_key
    )

    resp = requests.get(api_url)
    match_ids = resp.json()
    return match_ids      

#Given a match ID and mass region, get the data from the game
def get_match_data(match_id, mass_region, api_key):
    api_url = (
        "https://" + 
        mass_region + 
        ".api.riotgames.com/lol/match/v5/matches/" +
        match_id + 
        "?api_key=" + 
        api_key
    )
    
    #Continuously loop until it's successful
    while True:
        resp = requests.get(api_url)
        
        #When error 429, sleep for 10 seconds and then restart from the top of the "while" loop
        if resp.status_code == 429:
            print("Rate Limit hit, sleeping for 10 seconds")
            time.sleep(10)
            continue
        match_data = resp.json()
        return match_data      

#Given the match data and a players puuid, return the data about just them
def find_player_data(match_data, puuid):
    participants = match_data['metadata']['participants']
    player_index = participants.index(puuid)
    player_data = match_data['info']['participants'][player_index]
    return player_data

def gather_all_data(puuid, match_ids, mass_region, api_key):
    #Initialise an empty dictionary to store data for each game
    data = {
        'champion': [],
        'kills': [],
        'deaths': [],
        'assists': [],
        'win': []
    }
    for match_id in match_ids:
        #Run the two functions to get the player data from the match ID
        match_data = get_match_data(match_id, mass_region, api_key)
        player_data = find_player_data(match_data, puuid)

        #Assign the wanted variables
        champion = player_data['championName']
        k = player_data['kills']
        d = player_data['deaths']
        a = player_data['assists']
        win = player_data['win']

        #Add to dataset
        data['champion'].append(champion)
        data['kills'].append(k)
        data['deaths'].append(d)
        data['assists'].append(a)
        data['win'].append(win)    
    
    df = pandas.DataFrame(data)
    
    return df

#Master function to run everything
def master_function(summoner_name, region, mass_region, no_games, queue_id, api_key):
    puuid = get_puuid(summoner_name, region, api_key)
    match_ids = get_match_ids(puuid, mass_region, no_games, queue_id, api_key)
    df = gather_all_data(puuid, match_ids, mass_region, api_key)
    return df

df = master_function(summoner_name, region, mass_region, no_games, queue_id, api_key)

#Function to find and print data from most recent game
def most_recent(summoner_name, region, mass_region, no_games, queue_id, api_key):
    puuid = get_puuid(summoner_name, region, api_key)
    match_ids = get_match_ids(puuid, mass_region, 1, queue_id, api_key)
    match_data = get_match_data(match_ids[0], mass_region, api_key)
    participants = match_data['metadata']['participants']
    print("Most Recent Game:")
    print("Team 1:", end = " ")
    #Player counter
    i = 1

    #Has match result been printed
    result = False

    #Iterate through list
    for x in range(len(participants)):
        player_data = match_data['info']['participants'][x]
        summonername = player_data['summonerName']
        champion = player_data['championName']
        k = player_data['kills']
        d = player_data['deaths']
        a = player_data['assists']
        team = player_data['teamId']
        win = player_data['win']

        #Print only if same team
        if(team == 100):

            #Print match result
            if(result == False) and (win == True):
                print("Won")
                result = True
            elif(result == False) and (win == False):
                print("Lost")
                result = True

            #Print stats
            print("Player", i, ":", summonername, "| Champion :", champion, "| KDA :", k, "/", d, "/", a)

            #Increase player count
            i += 1
    print()
    print("Team 2:", end = " ")
    #Player counter
    i = 1

    #Has match result been printed
    result = False

    #Iterate through list
    for x in range(len(participants)):
        player_data = match_data['info']['participants'][x]
        summonername = player_data['summonerName']
        champion = player_data['championName']
        k = player_data['kills']
        d = player_data['deaths']
        a = player_data['assists']
        team = player_data['teamId']

        #Print only if same team
        if(team == 200):

            #Print match result
            if(result == False) and (win == True):
                print("Won")
                result = True
            elif(result == False) and (win == False):
                print("Lost")
                result = True

            #Print stats
            print("Player", i, ":", summonername, "| Champion :", champion, "| KDA :", k, "/", d, "/", a)

            #Increase player count
            i += 1

#Print introduction
print()
print("Hello", summoner_name, "of", region.upper())
print("Here are some interesting statistics about your last", no_games, queue_type, "games")

#Create a count column
df['count'] = 1 

#Get the average of every column and sum the count                                   
champ_df = df.groupby('champion').agg({'kills': 'mean', 'deaths': 'mean', 'assists': 'mean', 'win': 'mean', 'count': 'sum'})

#Reset in the index to still use the "champion" column
champ_df.reset_index(inplace=True)

#Limit it to only champions where at least 2 games were played
champ_df = champ_df[champ_df['count'] >= 2]

#Kda column
champ_df['kda'] = (champ_df['kills'] + champ_df['assists']) / champ_df['deaths']

#Sort from highest to lowest by kda
champ_df = champ_df.sort_values('kda', ascending=False) # ascending determines whether it's highest to lowest or vice-versa

#Assign first and last row to variables
best_row = champ_df.iloc[0] 
worst_row = champ_df.iloc[-1] 

#Print kda info
print("Your best KDA is on", best_row['champion'], "with a KDA of", best_row['kda'], "over", best_row['count'], "game/s")
print("Your worst KDA is on", worst_row['champion'], "with a KDA of", worst_row['kda'], "over", worst_row['count'], "game/s")

#Sort by count
champ_df = champ_df.sort_values('count', ascending=False)

#Most played champ
row = champ_df.iloc[0]

#Assign and format winrate
win_rate = row['win']
win_rate = str(round(win_rate * 100, 1)) + "%"

#Print most played and winrate info
print("Your most played Champion is", row['champion'], "with", row['count'], 'game/s', "and an average winrate of", win_rate)

#Sort by highest kills
highest_kills = df.sort_values('kills', ascending=False)
row = highest_kills.iloc[0]

#Print highest kills info
print("Your highest kill game was with", row['champion'], "where you had", row['kills'], "kills")

print()
most_recent(summoner_name, region, mass_region, 1, queue_id, api_key)