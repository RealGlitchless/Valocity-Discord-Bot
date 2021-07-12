import discord
from valorant import Client
from discord.ext import commands
from discord.utils import get
import os
import keep_alive
import requests
from datetime import datetime
from replit import db

# Prefix for commands
prefix = "!vc "
bot = commands.Bot(command_prefix=prefix)
ValoKey = os.environ['VALORANT KEY']
valorant = Client(ValoKey, locale='en-US', region='eu', route='europe')

# When BOT starts up
@bot.event
async def on_ready():
  # Set game to the string
  await bot.change_presence(activity=discord.Game('Brug "!vc commands" for at se alle commands'))
  # Confirm start up with print in console
  print('Logged in as: {0.user}'.format(bot))

@bot.command()
async def commands(help):
  userId = help.author.id
  user = await bot.fetch_user(str(userId))
  await user.send("Du kan bruge følgende kommandoer med '!vc':\nlink [USERNAME]#[TAG] - tilføje din konto til databasen for at bruge commands såsom riotid, rank og seneste\nunlink - Fjerner din konto fra databasen\nriotid {fx. @Soerensen} - Finder dit eller andens Riot ID fra databasen\nrank {fx. @Soerensen} - Få din eller en andens nuværende rank og rating. Denne kommand ændre også din rank rolle\nseneste - Få detaljer om din seneste match direkte i en privat besked\nsøg [USERNAME]#[TAG] - Søg på enhver Valorant spiller i EU\noffers - Se de nuværende skins som er på tilbud i butikken\ntop10  - Se hvem der er top 10 lige nu på leaderboardet i EU\nact - Se hvilken episode og act vi er i og hvor lang tid der er tilbage\nagents - Se de tilgængelige agents som er i Valorant lige nu\nmaps - Se de tilgængelige maps i Valorant lige nu\nstatus - Se hvad status er på Valorant serverene\n[] = påkrævet\n{} = frivilligt")

@bot.command()
async def agents(Agents):
  # Get all agents in game
  try:
    agents = valorant.get_characters()
    tempAgentList = []
    agentList = []
    for agent in agents:
      # Removes invalid data
      if agent.name != "Null UI Data!":
        tempAgentList.append(agent.name)
    # Removes duplicates (e.g. 2 Sovas would appear)
    for item in tempAgentList:
      if not item in agentList: 
        agentList.append(item)     
    await Agents.send("Disse agenter er tilgængelig lige nu: " + ", ".join(agentList))
  except:
    await Agents.send("Kunne ikke få information på de agents der er i spilet")
    return

@bot.command()
async def maps(Maps):
  # Få alle maps som er i Valorant
  try:
    maps = valorant.get_maps()
    mapList = []
    tempMapList = []
    for map in maps:
      # Removes invalid data
      if map.name != "Null UI Data!" or map.name != "The Range":
        tempMapList.append(map.name)
    # Removes duplicates
    for item in tempMapList:
      if not item in mapList: 
        mapList.append(item)
    await Maps.send("De aktive maps er lige nu: " + ", ".join(mapList))
  except:
    await Maps.send("Kunne ikke få maps i Valorant")
    return

@bot.command()
async def status(Status):
  # Get current status of valorant
  try:
    r = requests.get(f"https://api.henrikdev.xyz/valorant/v1/store-featured")
    json_data = r.json()
    data = json_data.get("data")
    valoStatus = data.get("maintenances")
    valoSeverity = data.get("incidents")
    if len(valoStatus) != 0:
      await Status.send("Status for Valorant er lige nu: " + valoStatus + "\nAlvorligheden: " + valoSeverity)
    else:
      await Status.send("Der er lige nu ingen problemer med Valorant")
  except:
    await Status.send("Kunne ikke få status på Valorant")
    return
  
@bot.command()
async def act(Act):
  # Get time left of season
  episodeAndAct = []
  endTimeList = []
  endDateList = []
  try:
    # Get all episodes and act
    r = requests.get(f"https://valorant-api.com/v1/seasons")
    json_data = r.json()
    data = json_data.get("data")
    # Get current date and time
    dateToday = datetime.now()
    # Only get date
    dateToday = dateToday.strftime("%Y-%m-%d")
    # Get start and end time for each season
    for item in data:
      startTime = item.get("startTime")
      startDate= startTime.split("T")
      startDate = startDate[0]
      endTime = item.get("endTime")
      endTime = endTime.split("T")
      endDate = endTime[0]
      endTime = endTime[1]
      # Check if item is between the starting and ending date. If so, put into list
      if startDate < dateToday < endDate:
        endTimeList.append(endTime)
        endDateList.append(endDate)
        displayName = item.get("displayName")
        episodeAndAct.append(displayName)

    await Act.send(f"Vi er lige nu i {episodeAndAct[0]} {episodeAndAct[1]}.\nEpisoden slutter den {endDateList[0]} kl. {endTimeList[0].rstrip(endTimeList[0][-1])}.\nActen slutter den {endDateList[1]} kl. {endTimeList[1].rstrip(endTimeList[1][-1])}.")
  except: 
    await Act.send("Kunne ikke få Act fra API")
    return

@bot.command()
async def top10(Leaderboard):
  try: 
  # Get act ID
    act = valorant.get_current_act()
  except:
    await Leaderboard.send("Kunne ikke få Act fra API")
    return
  
  actId = act.id
  
  try:
  # Get leaderboard for top 10 players with actid
    lb = valorant.get_leaderboard(10, 0, actId)

    players = lb.players
    playerList = []
    nameList = []
    rankList = []
    numofWinsList = []
    ratingList = []
    # Only get players and remove act id
    for item in players:
      playerList.append(item)
    #Get name, rank rating and number of wins for each player in top 10 and put into lists
    for player in playerList:
      name = player.gameName
      rank = player.leaderboardRank
      rating = player.rankedRating
      numOfWins = player.numberOfWins
      rankList.append(rank)
      nameList.append(name)
      ratingList.append(rating)
      numofWinsList.append(numOfWins)

    # Take data from lists and convert it to a message
    await Leaderboard.send(f"Top 10 på leaderboard er lige nu:\n{rankList[0]}. {nameList[0]} med {ratingList[0]} rating og {numofWinsList[0]} wins\n{rankList[1]}. {nameList[1]} med {ratingList[1]} rating og {numofWinsList[1]} wins\n{rankList[2]}. {nameList[2]} med {ratingList[2]} rating og {numofWinsList[2]} wins\n{rankList[1]}. {nameList[3]} med {ratingList[3]} rating og {numofWinsList[3]} wins\n{rankList[4]}. {nameList[4]} med {ratingList[4]} rating og {numofWinsList[4]} wins\n{rankList[5]}. {nameList[5]} med {ratingList[5]} rating og {numofWinsList[5]} wins\n{rankList[6]}. {nameList[6]} med {ratingList[6]} rating og {numofWinsList[6]} wins\n{rankList[7]}. {nameList[7]} med {ratingList[7]} rating og {numofWinsList[7]} wins\n{rankList[8]}. {nameList[8]} med {ratingList[8]} rating og {numofWinsList[8]} wins\n{rankList[9]}. {nameList[9]} med {ratingList[9]} rating og {numofWinsList[9]} wins")
  
  except:
    await Leaderboard.send("Kunne ikke få leaderboard fra API")
    return

@bot.command()
async def offers(offers):
  offerList = []
  skinIdList = []
  skinNameList = []
  skinDict = {}
  skinOnSale = []

  try:
    # Get featured skins
    r = requests.get(f"https://api.henrikdev.xyz/valorant/v1/store-featured")
    json_data = r.json()
    data = json_data.get("data")
    featureBundle = data.get("FeaturedBundle")
    bundle = featureBundle.get("Bundle")
    itemsData = bundle.get("Items")
  except:
    await offers.send("Kunne ikke få adgang til de featured skins")
    return

  for item in itemsData:
    skinItem = item.get("Item")
    itemId = skinItem.get("ItemID")
    offerList.append(itemId)

  try:
    # Get all skins
    r1= requests.get(f"https://valorant-api.com/v1/weapons/skins")
    skinData = r1.json()
    data = skinData.get("data")
  except:
    await offers.send("Kunne ikke få adgang til skins databasen")
    return

  try:
    for item in data:
      levels = item.get("levels")
      name = levels[0].get("displayName")
      skinId = levels[0].get("uuid")
      skinNameList.append(name)
      skinIdList.append(skinId)
      skinDict.update({skinId: name})
  except:
    await offers.send("Kunne ikke finde finde skinsene")
    return
  
  # Compare feature skin ID's with all skin ID's
  skinDictList = list(skinDict.keys())
  skinDictList.sort()
  for key in skinDictList:
    if key in offerList:
      skin = skinDict.get(key)
      skinOnSale.append(skin)
  
  if len(skinOnSale) == 0:
    await offers.send("Kunne ikke finde nogen skins i databasen som matcher dem til salg") 
  
  else:
    skinSale_str = (", ".join(skinOnSale))

    try:
    # Time left of bundle
      timeLeftSec = featureBundle.get("BundleRemainingDurationInSeconds")
      s = timeLeftSec
      days = int(s / 60 / 60 / 24 % 365)
      hours = int(s / 60 / 60 % 24)   
      minutes =int(s / 60 % 60)    
      secounds = int(s % 60)      
      timeLeft = "{} dage, {} timer, {} minutter og {} sekunder".format(days, hours, minutes, secounds)

      # Send the current available skins in message with timer
      await offers.send("Lige nu er der følgende skins på tilbud:\n{}.\nTilbuddet er tilgængeligt de næste {}.\nSkynd dig at købe dem!".format(skinSale_str, timeLeft))

    except:
      await offers.send("Lige nu er der følgende skins på tilbud:\n{}.\nSkynd dig at købe dem!".format(skinSale_str))
      return
      
@bot.command()
async def søg(Search, *, nameAndTag):
  name = nameAndTag.split("#")
  userName = name[0]
  userTag = name[1]
  # Get info from API with username and tagline
  try:
    r= requests.get(f"https://api.henrikdev.xyz/valorant/v1/mmr/eu/{userName}/{userTag}")
  except:
    await Search.send("Kunne ikke finde kontoen")
    return

  try:
    # Get Rank and rating from API
    accData = r.json()
    data = accData.get("data")
    rank = data.get("currenttierpatched")
    rating = data.get("ranking_in_tier")

  except:
    await Search.send("Kunne ikke få data fra API'en")
    return
    
  await Search.send(f"{userName}#{userTag} er lige nu i {rank} med {rating} rating")

@bot.command()
async def link(Link, *, nameAndTag):
  name = nameAndTag.split("#")
  userName = name[0]
  userTag = name[1]
  userId = Link.author.id
  keys = db.keys()
  
  # Check if Discord ID is already in db
  if keys.__contains__(str(userId)):
    await Link.send("Der er allerede en Riot konto tilknyttet din Discord profil. Brug '!V unlink' for at frakobel din Riot konto med din Discord profil")
    return

  try:
    r = requests.get(f"https://api.henrikdev.xyz/valorant/v1/mmr/eu/{userName}/{userTag}")
    # Get data from API
    data = r.json()
    status = data.get("status")
    if status == "200":
      try:
        db[userId] = nameAndTag
        await Link.send(f"Kontoen {nameAndTag} er blevet tilknyttet din Discord konto")
      
      except:
        await Link.send("Kunne ikke tilføje kontoen til databasen")
        return
    else:
      await Link.send("Kunne ikke finde kontoen")
      return
  except:
    await Link.send("Kunne ikke få data fra API'en")
    return

@bot.command()
async def unlink(Unlink):
  userId = Unlink.author.id
  try:
    del db[str(userId)]
    await Unlink.send("Kontoen er blevet slettet")
    return
  except:
    await Unlink.send("Kontoen kunne ikke slettes fra databasen eller eksistere den ikke i databasen")
    return

@bot.command()
async def riotid(Id, *, user: discord.User = None):
  if user == None:
    userId = Id.author.id
    try:
      # Get value of key which is the discord ID
      riotId = db[str(userId)]
      await Id.send(f"Dit Riot ID er {riotId}")
    except:
      await Id.send("Din konto er ikke tilknyttet din Discord profil endnu. Brug '!V link [USERNAME]#[TAG]' for at tilknytte din konto")
    return

  else:
    userId = user.id
    try:
      riotId = db[str(userId)]
      await Id.send(f"Riot ID for {user} er {riotId}")
    except:
      await Id.send("Kontoen er ikke registeret i databasen")

@bot.command()
async def rank(Rank, *, user: discord.User = None):
  if user == None:
    userId = Rank.author.id
    try:
      riotId = db[str(userId)]
      name = riotId.split("#")
      userName = name[0]
      userTag = name[1]
    except:
      await Rank.send("Din konto er ikke tilknyttet din Discord profil endnu. Brug '!V link [USERNAME]#[TAG]' for at tilknytte din konto")
      return

    try: 
      r = requests.get(f"https://api.henrikdev.xyz/valorant/v1/mmr/eu/{userName}/{userTag}")
    except:
      await Rank.send("Kunne ikke hente data fra API")
    # Get Rank and rating from API
    try:
      accData = r.json()
      data = accData.get("data")
      rank = data.get("currenttierpatched")
      rating = data.get("ranking_in_tier")
    except:
      rank = "Unranked"
      pass
      
    try: 
      member = Rank.author

      if rank == "Unranked":
        role = get(member.guild.roles, name = "Unranked")
        if rank != role:
          for item in member.guild.roles:
            if not str(item) == "Admins" or str(item) == "Faceit" or str(item) == "Server Booster" or str(item) == "📺 ON AIR 📺":
              try:
                await member.remove_roles(item)
              except: pass
              await member.add_roles(role)

      if rank == "Iron 1" or rank == "Iron 2" or rank == "Iron 3":
        role = get(member.guild.roles, name = "Iron")
        rankSplit = rank.split(" ")
        if rankSplit[0] != role:
          for item in member.guild.roles:
            if not str(item) == "Admins" or str(item) == "Faceit" or str(item) == "Server Booster" or str(item) == "📺 ON AIR 📺":
              try:
                await member.remove_roles(item)
              except: pass
              await member.add_roles(role)

      if rank == "Bronze 1" or rank == "Bronze 2" or rank == "Bronze 3":
        role = get(member.guild.roles, name = "Bronze")
        rankSplit = rank.split(" ")
        if rankSplit[0] != role:
          for item in member.guild.roles:
            if not str(item) == "Admins" or str(item) == "Faceit" or str(item) == "Server Booster" or str(item) == "📺 ON AIR 📺":
              try:
                await member.remove_roles(item)
              except: pass
              await member.add_roles(role)

      if rank == "Silver 1" or rank == "Silver 2" or rank == "Silver 3":
        role = get(member.guild.roles, name = "Silver")
        rankSplit = rank.split(" ")
        if rankSplit[0] != role:
          for item in member.guild.roles:
            if not str(item) == "Admins" or str(item) == "Faceit" or str(item) == "Server Booster" or str(item) == "📺 ON AIR 📺":
              try:
                await member.remove_roles(item)
              except: pass
              await member.add_roles(role)

      if rank == "Gold 1" or rank == "Gold 2" or rank == "Gold 3":
        role = get(member.guild.roles, name = "Gold")
        rankSplit = rank.split(" ")
        if rankSplit[0] != role:
          for item in member.guild.roles:
            if not str(item) == "Admins" or str(item) == "Faceit" or str(item) == "Server Booster" or str(item) == "📺 ON AIR 📺":
              try:
                await member.remove_roles(item)
              except: pass
              await member.add_roles(role)

      if rank == "Platinum 1" or rank == "Platinum 2" or rank == "Platinum 3":
        role = get(member.guild.roles, name = "Platinum")
        rankSplit = rank.split(" ")
        if rankSplit[0] != role:
          for item in member.guild.roles:
            if not str(item) == "Admins" or str(item) == "Faceit" or str(item) == "Server Booster" or str(item) == "📺 ON AIR 📺":
              try:
                await member.remove_roles(item)
              except: pass
              await member.add_roles(role)

      if rank == "Diamond 1" or rank == "Diamond 2" or rank == "Diamond 3":
        role = get(member.guild.roles, name = "Diamond")
        rankSplit = rank.split(" ")
        if rankSplit[0] != role:
          for item in member.guild.roles:
            if not str(item) == "Admins" or str(item) == "Faceit" or str(item) == "Server Booster" or str(item) == "📺 ON AIR 📺":
              try:
                await member.remove_roles(item)
              except: pass
              await member.add_roles(role)

      if rank == "Immortal":
        role = get(member.guild.roles, name = "Immortal")
        if rank != role:
          for item in member.guild.roles:
            if not str(item) == "Admins" or str(item) == "Faceit" or str(item) == "Server Booster" or str(item) == "📺 ON AIR 📺":
              try:
                await member.remove_roles(item)
              except: pass
              await member.add_roles(role)

      if rank == "Radiant":
        role = get(member.guild.roles, name = "Radiant")
        if rank != role:
          for item in member.guild.roles:
            if not str(item) == "Admins" or str(item) == "Faceit" or str(item) == "Server Booster" or str(item) == "📺 ON AIR 📺":
              try:
                await member.remove_roles(item)
              except: pass
              await member.add_roles(role)

    except:
      await Rank.send("Kunne ikke tilføje rolle til din Discord konto. Kontakt venligst Holm eller Soerensen")
      pass

    await Rank.send(f"Din konto, {userName}#{userTag}, er lige nu i {rank} med {rating} rating")


  else:
    userId = user.id
    try:
      riotId = db[str(userId)]
    except:
      await Rank.send("Kontoen er ikke registeret i databasen")
      return
    name = riotId.split("#")
    userName = name[0]
    userTag = name[1]
    # Get info from API with username and tagline
    try:
      r = requests.get(f"https://api.henrikdev.xyz/valorant/v1/mmr/eu/{userName}/{userTag}")
    except:
      await Rank.send("Kunne ikke finde kontoen")
      return

    try:
      # Get Rank and rating from API
      accData = r.json()
      data = accData.get("data")
      rank = data.get("currenttierpatched")
      rating = data.get("ranking_in_tier")

    except:
      await Rank.send("Kunne ikke få data fra API'en")
      return
      
    await Rank.send(f"{userName}#{userTag} er lige nu i {rank} med {rating} rating")

@bot.command()
async def seneste(recent):
  redTeam = []
  redTag = []
  redCharacter = []
  redRank = []
  redKills  = []
  redDeaths = []
  redAssist = []
  redAvgCS = []
  blueTeam = []
  blueTag = []
  blueCharacter = []
  blueRank = []
  blueKills = []
  blueDeaths = []
  blueAssist = []
  blueAvgCS = []

  userId = recent.author.id
  user = await bot.fetch_user(str(userId))
  
  try:
    riotId = db[str(userId)]
  except:
    await recent.send("Din konto er ikke tilknyttet din Discord profil endnu. Brug '!V link [USERNAME]#[TAG]' for at tilknytte din konto")
    return
  name = riotId.split("#")
  userName = name[0]
  userTag = name[1]

  try:
    r = requests.get(f"https://api.henrikdev.xyz/valorant/v3/matches/eu/{userName}/{userTag}")
    json_data = r.json()
    data = json_data.get("data")
  except:
    await recent.send("Kunne ikke få data fra API'en")
    return  

  metadata = data[0].get("metadata")
  map = metadata.get("map")
  mode = metadata.get("mode")
  roundsPlayer = metadata.get("rounds_played")

  players = data[0].get("players")
  red = players.get("red")
  blue = players.get("blue")
  for item in red:
    name = item.get("name")
    redTeam.append(name)
    tag = item.get("tag")
    redTag.append(tag)
    stats  = item.get("stats")
    redKills.append(stats.get("kills"))
    redDeaths.append(stats.get("deaths"))
    redAssist.append(stats.get("assists"))
    redCharacter.append(item.get("character"))
    score = stats.get("score")
    redAvgCS.append(score//roundsPlayer)

    try:
      nameAndTagReq = requests.get(f"https://api.henrikdev.xyz/valorant/v1/mmr/eu/{name}/{tag}")
    except:
      await recent.send("Kunne ikke få data fra API'en")
      return  

    try:
      nameAndTagData = nameAndTagReq.json()
      nameAndTagData = nameAndTagData.get("data")
      rank = nameAndTagData.get("currenttierpatched")
    except:
      rank = "Unranked"
      pass

    redRank.append(rank)

  for item in blue:
    name = item.get("name")
    blueTeam.append(name)
    tag = item.get("tag")
    blueTag.append(tag)
    stats  = item.get("stats")
    blueKills.append(stats.get("kills"))
    blueDeaths.append(stats.get("deaths"))
    blueAssist.append(stats.get("assists"))
    blueCharacter.append(item.get("character"))
    score = stats.get("score")
    blueAvgCS.append(score//roundsPlayer)

    try:
      nameAndTagReq = requests.get(f"https://api.henrikdev.xyz/valorant/v1/mmr/eu/{name}/{tag}")
    except:
      await recent.send("Kunne ikke få data fra API'en")
      return  

    try:
      nameAndTagData = nameAndTagReq.json()
      nameAndTagData = nameAndTagData.get("data")
      rank = nameAndTagData.get("currenttierpatched")
    except:
      rank = "Unranked"
      pass

    blueRank.append(rank)

  teams = data[0].get("teams")
  redDetails = teams.get("red")
  blueDetails = teams.get("blue")
  redWonRounds = redDetails.get("rounds_won")
  blueWonRounds = blueDetails.get("rounds_won")

  await user.send(f"------------------------------ MATCH SUMMARY ------------------------------\n**Hold 1:**\n{redTeam[0]}#{redTag[0]} // {redRank[0]} // {redCharacter[0]} // K/D/A: {redKills[0]}/{redDeaths[0]}/{redAssist[0]} // Combat score: {redAvgCS[0]}\n{redTeam[1]}#{redTag[1]} // {redRank[1]} // {redCharacter[1]} // K/D/A: {redKills[1]}/{redDeaths[1]}/{redAssist[1]} // Combat score: {redAvgCS[1]}\n{redTeam[2]}#{redTag[2]} // {redRank[2]} // {redCharacter[2]} // K/D/A: {redKills[2]}/{redDeaths[2]}/{redAssist[2]} // Combat score: {redAvgCS[2]}\n{redTeam[3]}#{redTag[3]} // {redRank[3]} // {redCharacter[3]} // K/D/A: {redKills[3]}/{redDeaths[3]}/{redAssist[3]} // Combat score: {redAvgCS[3]}\n{redTeam[4]}#{redTag[4]} // {redRank[4]} // {redCharacter[4]} // K/D/A: {redKills[4]}/{redDeaths[4]}/{redAssist[4]} // Combat score: {redAvgCS[4]}\n\n**Hold 2:**\n{blueTeam[0]}#{blueTag[0]} // {blueRank[0]} // {blueCharacter[0]} // K/D/A: {blueKills[0]}/{blueDeaths[0]}/{blueAssist[0]} // Combat score: {blueAvgCS[0]}\n{blueTeam[1]}#{blueTag[1]} // {blueRank[1]} // {blueCharacter[1]} // K/D/A: {blueKills[1]}/{blueDeaths[1]}/{blueAssist[1]} // Combat score: {blueAvgCS[1]}\n{blueTeam[2]}#{blueTag[2]} // {blueRank[2]} // {blueCharacter[2]} // K/D/A: {blueKills[2]}/{blueDeaths[2]}/{blueAssist[2]} // Combat score: {blueAvgCS[2]}\n{blueTeam[3]}#{blueTag[3]} // {blueRank[3]} // {blueCharacter[3]} // K/D/A: {blueKills[3]}/{blueDeaths[3]}/{blueAssist[3]} // Combat score: {blueAvgCS[3]}\n{blueTeam[4]}#{blueTag[4]} // {blueRank[4]} // {blueCharacter[4]} // K/D/A: {blueKills[4]}/{blueDeaths[4]}/{blueAssist[4]} // Combat score: {blueAvgCS[4]}\n\nMode: {mode}\nKampen sluttede {str(redWonRounds)} - {str(blueWonRounds)} på {map}")
  await recent.send("PB sendt med detaljer")

keep_alive.keep_alive()
bot.run(os.getenv('DISCORD TOKEN'))