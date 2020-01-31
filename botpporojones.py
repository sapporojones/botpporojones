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



#imports
import os
import random
import discord
import requests
import json
import praw
from datetime import datetime, tzinfo, timedelta
import pytz

from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

#pull ins from the env file
token = os.getenv('DISCORD_TOKEN')
weather_key = os.getenv('API_KEY')
stockmarket_key = os.getenv('STOCKMARKET_KEY')

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
	reddit = praw.Reddit(client_id='{client_id}',
                     client_secret='{client_secret}',
                     password='{reddit_password}'',
                     user_agent='testscript by /u/sapporojones',
                     username='{reddit_username}')
	random_submission = reddit.subreddit(sub_reddit).random()
	submission_url = reddit.submission(random_submission).url
	content_url = "https://www.reddit.com/r/" + sub_reddit + "/" + str(random_submission) 
	await ctx.send(submission_url)


@bot.command(name='time', help='current time for a variety of timezones')
async def time(ctx):
	base_url = "http://worldtimeapi.org/api/timezone/"

	global_json = requests.get(base_url + "/America/Los_Angeles").json()
	global_utc = global_json['unixtime']

	westutc = global_utc - 28800
	uswest = datetime.utcfromtimestamp(westutc).strftime('%H:%M')

	cstutc = global_utc - 21600
	uscent = datetime.utcfromtimestamp(cstutc).strftime('%H:%M')

	estutc = global_utc - 18000
	useast = datetime.utcfromtimestamp(estutc).strftime('%H:%M')

	ukutc = global_utc
	uktz = datetime.utcfromtimestamp(ukutc).strftime('%H:%M')

	ruutc = global_utc + 10800
	rutz = datetime.utcfromtimestamp(ruutc).strftime('%H:%M')

	auutc = global_utc + 39600
	autz = datetime.utcfromtimestamp(auutc).strftime('%H:%M')

	line1 = "**West Coast: **" + uswest + "\n"
	line2 = "**US Central: **" + uscent + "\n"
	line3 = "**US East: **" + useast + "\n"
	line4 = "**London/GMT: **" + uktz + "\n"
	line5 = "**Moscow, RU: **" + rutz + "\n"
	line6 = "**Sydney, AU: **" + autz
	response = line1 + line2 + line3 + line4 + line5 + line6

#	response = "**West Coast: **" + uswest + "\n**Central TZ: **" + uscent + "\n**East TZ: **" + useast + "\n**UK Time/GMT: **" + uktz + "\n**Moscow: **" + rutz + "\n**AussieTZ: **" + autz




	await ctx.send(response)


bot.run(token)

