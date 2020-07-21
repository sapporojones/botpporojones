
#using bot commands now like a big boy
#bot sappo
#0.1 - initial work
#0.2 - conert to bot.commands
#0.3 - add weather command
#0.4 - add stock ticker lookup
#0.5 - add IP lookup
#0.6 - add reddit image pull and PRAW support
#0.7 - now pulling more info for stock quotes and has it properly formatted.  working on the ip command now to add google maps functionality
#0.8 - adding a time command
#0.9 - moving the PRAW reddit definition vars to .env where they are meant to live
#0.9.1 - beginning to add EVE ESI commands for various lookup functions using unknown ids

#imports
from __future__ import print_function
import os
import random
import discord
import requests
import json
import praw
from datetime import datetime, tzinfo, timedelta
import pytz
from bravado.client import SwaggerClient
import bravado.exception
from esipy import EsiApp
from esipy import EsiClient
from esipy import App
from discord.ext import commands
from dotenv import load_dotenv


esi_app = EsiApp()

#app = App.create(url="https://esi.evetech.net/latest/swagger.json?datasource=tranquility")

client = EsiClient(
    retry_requests=True,  # set to retry on http 5xx error (default False)
    headers={'User-Agent': 'rando eve user just lookin at stuff'},
    raw_body_only=False,  # default False, set to True to never parse response and only return raw JSON string content.
)

app = esi_app.get_latest_swagger

load_dotenv()

#pull ins from the env file
token = os.getenv('DISCORD_TOKEN')
weather_key = os.getenv('API_KEY')
stockmarket_key = os.getenv('STOCKMARKET_KEY')

#reddit pull ins from the env file
reddit_clientID = os.getenv('CLIENT_ID')
reddit_clientSecret = os.getenv('CLIENT_SECRET')
reddit_password = os.getenv('PASSWORD')
reddit_username = os.getenv('USERNAME')




#bot command modifier
bot = commands.Bot(command_prefix='!')



#begin bot commands
@bot.command(name='d100', help='Roll the d100 to determine the fate of the alliance.')
async def d100(ctx):
	roll = str(random.randint(1,100))
	response = 'You rolled a ' + roll
	await ctx.send(response)

@bot.command(name='create-channel', help='creates a text channel.')
@commands.has_role('admin')
async def create_channel(ctx, channel_name):
	guild = ctx.guild
	existing_channel = discord.utils.get(guild.channels, name=channel_name)
	if not existing_channel:
		print(f'Creating a new channel: {channel_name}')
		await guild.create_text_channel(channel_name)

@bot.command(name='weather', help='returns weather info for a given zip code')
async def weather(ctx, zip_code):
	base_url="http://api.openweathermap.org/data/2.5/weather?"
	complete_url = base_url + "appid=" + weather_key + "&zip=" + str(zip_code) + "&units=imperial"
	full_json = requests.get(complete_url).json()
	weather_description = full_json['weather'][0]['description']
	weather_temp = full_json['main']['temp']
	response = "The temperature at " + str(zip_code) + " is " + str(int(weather_temp)) + " degrees fahrenheit, the weather conditions are described as " + weather_description
	await ctx.send(response)

@bot.command(name='stock', help='stock quote lookup')
async def stock(ctx, ticker):
	query = 'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=' + ticker + '&apikey=' + stockmarket_key
	json_output = requests.get(query)
	data = json_output.json()
	response = "Here's some information about that security you requested:\n" + "The current price is: " + data["Global Quote"]["05. price"] + "\n" + "The current change is: " + data["Global Quote"]["09. change"] + "\n" + "The change percent of that is: " + data["Global Quote"]["10. change percent"] + "\n" + "The security opened at: " + data["Global Quote"]["02. open"] + "\n" + "The security closed last at: " + data["Global Quote"]["08. previous close"]
	await ctx.send(response)

@bot.command(name='ip', help='IP lookup info')
async def ip(ctx, address):
	base_url = 'https://ipapi.co/'
	json_url = base_url + address + '/json'
	get_data = requests.get(json_url)
	bulk_data = get_data.json()
	response1 = "Looking up info regarding " + bulk_data['ip'] + "\n"
	response2 = "City: " + bulk_data["city"] + "\n"
	response3 = "State or Region: " + bulk_data["region"] + "\n"
	response4 = "Country: " + bulk_data["country_name"] + "\n"
	response5 = "Organization: " + bulk_data["org"] + "\n"
	full_reply = "\n **HACKER MODE ENGAGED**\n" + response1 + response2 + response3 + response4 + response5 
	await ctx.send(full_reply)

@bot.command(name='r', help='returns posts from the specified subreddit')
async def r(ctx, sub_reddit):
	reddit = praw.Reddit(client_id=reddit_clientID,
                     client_secret=reddit_clientSecret,
                     password=reddit_password,
                     user_agent='testscript by /u/sapporojones',
                     username=reddit_username)
	random_submission = reddit.subreddit(sub_reddit).random()
	if random_submission.over_18 == True:
		submission_url = "Adult content detected, not posting"
	else:
		submission_url = reddit.submission(random_submission).url
	await ctx.send(submission_url)


@bot.command(name='time', help='current time for a variety of timezones')
async def time(ctx):
	base_url = "http://worldtimeapi.org/api/timezone/"

	pac_datetime_json = requests.get(base_url + "/America/Los_Angeles").json()
    pac_unix = pac_datetime_json['unixtime']
	uswest = datetime.utcfromtimestamp(pac_unix).strftime('%H:%M')

    mtn_datetime_json = requests.get(base_url + "/America/Denver").json()
    mtn_unix = mtn_datetime_json['unixtime']
    usmtn = datetime.utcfromtimestamp(mtn_unix).strftime('%H:%M')

    cent_datetime_json = requests.get(base_url + "/America/Detroit").json()
    cent_unix = cent_datetime_json['unixtime']
    uscent = datetime.utcfromtimestamp(cent_unix).strftime('%H:%M')

    east_datetime_json = requests.get(base_url + "/America/New_York").json()
    east_unix = east_datetime_json['unixtime']
    useast = datetime.utcfromtimestamp(east_unix).strftime('%H:%M')

    uk_datetime_json = requests.get(base_url + "/Europe/London").json()
    uk_unix = uk_datetime_json['unixtime']
    uktz = datetime.utcfromtimestamp(uk_unix).strftime('%H:%M')

    ru_datetime_json = requests.get(base_url + "/Europe/Moscow").json()
    ru_unix = ru_datetime_json['unixtime']
    rutz = datetime.utcfromtimestamp(ru_unix).strftime('%H:%M')

    au_datetime_json = requests.get(base_url + "/Australia/Sydney").json()
    au_unix = au_datetime_json['unixtime']
    autz = datetime.utcfromtimestamp(au_unix).strftime('%H:%M')

	line1 = "**West Coast: **" + uswest + "\n"
    line2 = "**US Mountain: **" + usmtn + "\n"
	line3 = "**US Central: **" + uscent + "\n"
	line4 = "**US East: **" + useast + "\n"
	line5 = "**London/GMT: **" + uktz + "\n"
	line6 = "**Moscow, RU: **" + rutz + "\n"
	line7 = "**Sydney, AU: **" + autz
	response = line1 + line2 + line3 + line4 + line5 + line6 + line7

	await ctx.send(response)

@bot.command(name='pilot', help='[RESTRICTED]get various urls about a given pilot name')
@commands.has_role('admin')
async def pilot(ctx, characterName):
	client = SwaggerClient.from_url('https://esi.evetech.net/latest/swagger.json')               
	charResults = client.Search.get_search(                                                      
        	search=characterName, 
        	categories=['character'],
	        strict=True,                                                                       
	        ).result()['character']                                                            

	if len(charResults) <= 0: raise Exception("Character not found")                             

	characterId = charResults[0]
	characterId = str(characterId)
	line1 = "**PILOT SEARCH RESULTS:**" + "\n"
	line2 = "**ZKB:** https://zkillboard.com/character/" + characterId + '/' + '\n'
	line3 = "**EVEWHO:** https://evewho.com/character/" + characterId + "/" + "\n"
	line4 = "**TEST Auth:** https://auth.pleaseignore.com/eve/character/" + characterId + "/" + "\n"
	response = line1 + line2 + line3 + line4

	await ctx.send(response)

@bot.command(name='corp', help='get various urls about a given corp')
async def corp(ctx, corporationName):
        client = SwaggerClient.from_url('https://esi.evetech.net/latest/swagger.json')
        corpResults = client.Search.get_search(
                search=corporationName,
                categories=['corporation'],
                strict=True,
                ).result()['corporation']

        if len(corpResults) <= 0: raise Exception("Corporation not found")

        corporationId = corpResults[0]
        corporationId = str(corporationId)
        line1 = "**CORP SEARCH RESULTS:**" + "\n"
        line2 = "**ZKB:** https://zkillboard.com/corporation/" + corporationId + '/' + '\n'
        line3 = "**EVEWHO:** https://evewho.com/corporation/" + corporationId + "/" + "\n"
        line4 = "**DOTLAN:** http://evemaps.dotlan.net/corp/" + corporationId + "/" + "\n"
        response = line1 + line2 + line3 + line4

        await ctx.send(response)

@bot.command(name='kick', help='kick a given user')
@commands.has_role('admin')
async def kick(ctx, user: discord.Member):
	await ctx.guild.kick(user)
	await ctx.send('**User has been removed**')

@bot.command(name='shlookup', help='get info on a pilot')
async def shlookup(ctx, pilot_name):
    #channel = message.channel
    pilot_lookup = app.op['post_universe_ids'](names=pilot_name)
    response = client.request(pilot_lookup, raw_body_only=True)
    response_data = response.raw
    char_json_response = json.loads(response_data)
    char_id = char_json_response["characters"][0]["id"]
    
    zkb_base_url = "https://zkillboard.com/api/stats/characterID/" + str(char_id) + "/"
    zkb_response = requests.get(zkb_base_url)
    zkb_json_response = zkb_response.json()

    evewho_base_url = "https://evewho.com/api/character/" + str(char_id) + "/"
    evewho_response = requests.get(evewho_base_url)
    evewho_json_response = evewho_response.json()
    corporation_id = evewho_json_response["info"][0]["corporation_id"]
    
    corp_name_get_url = "https://esi.evetech.net/latest/corporations/" + str(corporation_id) + "/?datasource=tranquility"
    corp_name_response = requests.get(corp_name_get_url)
    corp_name_json_response = corp_name_response.json()
    
    corp_name = corp_name_json_response["name"]
    corp_member_count = corp_name_json_response["member_count"]
    corp_ticker = corp_name_json_response["ticker"]
    response = ""
    response +=  "\n" 
    response +=  f"{pilot_name} is id {char_id}" + "\n"
    response +=  "\n" 
    response +=  f"Here are some relevant urls for {pilot_name}:" + "\n"
    response +=  f"Zkill: https://zkillboard.com/character/{char_id}/"+ "\n" 
    response +=  f"EveWho: https://evewho.com/character/{char_id}/" + "\n" 
    response +=  f"TEST Auth https://auth.pleaseignore.com/eve/character/{char_id}/"  + "\n"
    response +=  "\n" 
    response +=  f"{pilot_name} is a member of {corp_name} which has the ticker {corp_ticker} and has {corp_member_count} members"  + "\n"
    response +=  f"Here are some relevant urls for {corp_name}:"  + "\n"
    response +=  f"Zkill: https://zkillboard.com/corporation/{corporation_id}/"  + "\n"
    response +=  f"EveWho: https://evewho.com/corporation/{corporation_id}/"  + "\n"
    response +=  f"Dotlan: http://evemaps.dotlan.net/corp/{corporation_id}/"  + "\n"
    response +=  "\n"  + "Pilot was born " + str(evewho_json_response['history'][0]['start_date']) + "\n"
    response +=  f"{pilot_name} has the following zkb stats:"  + "\n"

    try:
        solo_kills = str(zkb_json_response["soloKills"])
    except:
        solo_kills = str(0)

    response += ("Solo Kills: " + solo_kills) + "\n"
    
    try:
        solo_losses = str(zkb_json_response["soloLosses"])
    except:
        solo_losses = str(0)
    
    response += ("Solo Losses: " + solo_losses) + "\n"
    
    try:
        total_kills = str(zkb_json_response["shipsDestroyed"])

        #only execute this block if the character has kills
        zkb_kills_url = "https://zkillboard.com/api/kills/characterID/" + str(char_id) + "/"
        zkb_get_kills = requests.get(zkb_kills_url)
        zkb_kills_json = zkb_get_kills.json()
        last_kill_hash = zkb_kills_json[0]["zkb"]["hash"]
        last_kill_id_0 = zkb_kills_json[0]["killmail_id"]
        last_kill_url = "https://esi.evetech.net/latest/killmails/" + str(last_kill_id_0) + "/" + str(last_kill_hash) + "/?datasource=tranquility"
        last_kill_get = requests.get(last_kill_url)
        last_kill_date_json = last_kill_get.json()
        last_kill_datetime = last_kill_date_json["killmail_time"]
        last_kill_time = last_kill_datetime[0:10]

        try:

#           dd = datetime.utcnow().date() - date(int(last_kill_time[0:4]), int(last_kill_time[6:7]), int(last_kill_time[9:10]))
            dd = datetime.utcnow().date() - datetime.strptime(last_kill_time, '%Y-%m-%d').date()
            dd = dd.days
        except:
            dd = str(0)


    except:
        total_kills = str(0)
    
    response += "Total Kills: " + total_kills + "\n"
    
    try:
        total_losses = str(zkb_json_response["shipsLost"])

        #only execute this block if the character has losses
        zkb_losses_url = "https://zkillboard.com/api/losses/characterID/" + str(char_id) + "/"
        zkb_get_losses = requests.get(zkb_losses_url)
        zkb_losses_json = zkb_get_losses.json()
        last_loss_id_0 = zkb_losses_json[0]["killmail_id"]
        last_loss_hash = zkb_losses_json[0]["zkb"]["hash"]
        last_loss_get_url = "https://esi.evetech.net/latest/killmails/" + str(last_loss_id_0) + "/" + str(last_loss_hash) + "/?datasource=tranquility"
        last_loss_get = requests.get(last_loss_get_url)
        last_loss_date_json = last_loss_get.json()
        lldt = last_loss_date_json["killmail_time"]

        last_loss_time = lldt[0:10]
        try:

#           d1 = datetime.utcnow().date() - date(int(last_loss_time[0:4]), int(last_loss_time[6:7]), int(last_loss_time[9:10]))
            d1 = datetime.utcnow().date() - datetime.strptime(last_loss_time, '%Y-%m-%d').date()
            d1 = d1.days
        except:
            d1 = str(0)

    except:
        total_losses = str(0)

    response += "Total Losses: " + total_losses + "\n"
   
    response += "\n"

    try:
        response += f"Last reported on a kill on {last_kill_time} which was {dd} days ago"

        has_kill = 1
    except:
        response += "Character has never been on a kill"
        has_kill = 0
    try:
        response += f"Last reported on a loss on {last_loss_time} which was {d1} days ago"
        has_loss = 1
    except:
        response += "Character has never had a loss"
        has_loss = 0

    response += ("\n")

    if has_kill == 1:

        if total_kills == 1:
            last_kill_id_0 = zkb_kills_json[0]["killmail_id"]
            response += "Last kill:\n"
            response += f"https://zkillboard.com/kill/{last_kill_id_0}/" + "\n"
        else:
            try:
                last_kill_id_0 = zkb_kills_json[0]["killmail_id"]
                last_kill_id_1 = zkb_kills_json[1]["killmail_id"]
                last_kill_id_2 = zkb_kills_json[2]["killmail_id"]
                last_kill_id_3 = zkb_kills_json[3]["killmail_id"]
                last_kill_id_4 = zkb_kills_json[4]["killmail_id"]
                response += ("Last 5 kills:\n")
                response += (f"https://zkillboard.com/kill/{last_kill_id_0}/") + "\n"
                response += (f"https://zkillboard.com/kill/{last_kill_id_1}/") + "\n"
                response += (f"https://zkillboard.com/kill/{last_kill_id_2}/") + "\n"
                response += (f"https://zkillboard.com/kill/{last_kill_id_3}/") + "\n"
                response += (f"https://zkillboard.com/kill/{last_kill_id_4}/") + "\n"
            except:
                last_kill_id_0 = zkb_kills_json[0]["killmail_id"]
                response += ("Last kill:\n")
                response += (f"https://zkillboard.com/kill/{last_kill_id_0}/") + "\n"
    else:
        return

    response += ("\n")
    if has_loss == 1:
        if total_losses == 1:
            last_kill_id_0 = zkb_kills_json[0]["killmail_id"]
            response += ("Last loss:\n")
            response += (f"https://zkillboard.com/kill/{last_loss_id_0}/") + "\n"
        else:
            try:
                last_loss_id_0 = zkb_losses_json[0]["killmail_id"]
                last_loss_id_1 = zkb_losses_json[1]["killmail_id"]
                last_loss_id_2 = zkb_losses_json[2]["killmail_id"]
                last_loss_id_3 = zkb_losses_json[3]["killmail_id"]
                last_loss_id_4 = zkb_losses_json[4]["killmail_id"]
                response += ("Last 5 losses:\n") + "\n"
                response += (f"https://zkillboard.com/kill/{last_loss_id_0}/") + "\n"
                response += (f"https://zkillboard.com/kill/{last_loss_id_1}/") + "\n"
                response += (f"https://zkillboard.com/kill/{last_loss_id_2}/") + "\n"
                response += (f"https://zkillboard.com/kill/{last_loss_id_3}/") + "\n"
                response += (f"https://zkillboard.com/kill/{last_loss_id_4}/") + "\n"
            except:
                last_kill_id_0 = zkb_kills_json[0]["killmail_id"]
                response += ("Last loss:\n")
                response += (f"https://zkillboard.com/kill/{last_loss_id_0}/") + "\n"
    else:
        return
    corp_history = []
    i = len(evewho_json_response['history']) - 1
    while len(corp_history) < 10:
        corpid = evewho_json_response['history'][i]['corporation_id']
        try:
            corp_history.append(corpid)
            i -= 1
        except:
            return
    response += ("\nCorporate History: (up to last ten corps displayed)\n")
    for entity in corp_history:
        corp_name_get_url = "https://esi.evetech.net/latest/corporations/" + str(entity) + "/?datasource=tranquility"
        corp_name_response = requests.get(corp_name_get_url)
        corp_name_json_response = corp_name_response.json()
        corp_name = corp_name_json_response["name"]
        corp_print = "Character was in: " + str(corp_name)
        
        try:
            alice_id = corp_name_json_response["alliance_id"]
            alice_name_get_url = "https://esi.evetech.net/latest/alliances/" + str(alice_id) + "/?datasource=tranquility"
            alice_name_response = requests.get(alice_name_get_url)
            alice_name_json_response = alice_name_response.json()
            corp_print += " which is a member of " + str(alice_name_json_response["name"])
            response += (corp_print) + "\n"
        except:
            response += (corp_print) + "\n"
        
        
        
        #response += (str(entity))

    await ctx.send(response)







############################################
#code goes above here
############################################
bot.run(token)

