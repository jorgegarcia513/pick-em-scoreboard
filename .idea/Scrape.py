import os
import datetime
import random
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import logging
import discord
from dotenv import load_dotenv
from discord.ext import commands
import asyncio
from tabulate import tabulate

# Initialize inital values
reverians = ["SSBM Super", "Mr Predict", "Nitop", "Pandamoniaz"]
maldenites = ["Sheda", "racecar69", "PëëF"]

# Initialize logging file
now = datetime.datetime.now()
logging.basicConfig(filename= "logs\\" + str(now.year) + str(now.day) + str(now.month) + '.log')

# Initialize driver options
chrome_options = Options()
chrome_options.headless = True

def get_names_and_scores(driver):
    """
    Scape the scoreboard webpage for scores along with the associated player
    :param driver: webdriver
    :return: a list of names and scores
    """
    names = []
    scores = []
    rows = len(driver.find_elements(*(By.CSS_SELECTOR, "#list-container > div > div.rank-table.show-stage-both > table > tbody.stage-both > tr")))
    for x in range(1, rows + 1):
        name = driver.find_element_by_css_selector("#list-container div.rank-table.show-stage-both tbody.stage-specific.stage-both > tr:nth-child(" + str(x) + ") > .left.player-cell a")
        names.append(name.text)
        score = driver.find_element_by_css_selector("#list-container > div > div.rank-table.show-stage-both > table > tbody.stage-specific.stage-both > tr:nth-child(" + str(x) + ") > td.left.points-cell")
        scores.append(score.text)
    return [names, scores]

def tally_score(name_and_scores, reverians, maldenites):
    """
    Tally up scores based off members of the two teams
    :param name_and_scores: list of names and scores
    :param reverians: list of people in team 1
    :param maldenites: list of people in team 2
    :return: list containing team 1's score and team 2's score
    """
    reverian_score = 0
    maldenite_score = 0
    for x in range(0, len(names_and_scores[0])):
        if names_and_scores[0][x] in reverians:
            reverian_score += int(names_and_scores[1][x])
        elif names_and_scores[0][x] in maldenites:
            maldenite_score += int(names_and_scores[1][x])
    return [reverian_score, maldenite_score]

def get_high_score_index(names_and_scores):
    """
    Get the index of the max score
    :param names_and_scores: list of names and scores
    :return: index of max score
    """
    return names_and_scores[1].index(max(names_and_scores[1])) - 1

def generate_scoreboard(names_and_scores):
    """
    Generate a scoreboard as a string
    :param names_and_scores: list of names and scores
    :return: scoreboard
    """
    scores = tally_score(names_and_scores, reverians, maldenites)
    string1 = "Reverian vs. Maldenite World's Pick 'Em Scores"
    string1 += "\n=================================="
    string1 += "\nLeaderboard:"
    for x in range(0, len(names_and_scores[0])):
        string1 += "\n " + names_and_scores[0][x] + ": " + names_and_scores[1][x]
    string1 += "\n=================================="
    string1 += "\nTotals:"
    string1 += "\n Reverian Score: " + str(scores[0])
    string1 += "\n Maldenite Score: " + str(scores[1])
    string1 += "\n High Score: " + names_and_scores[0][get_high_score_index(names_and_scores)]
    return string1


# Initialize web driver
driver = webdriver.Chrome(executable_path="C:\\Users\\17815\\Documents\\WorldsScore\\chromedriver.exe",   options=chrome_options)
driver.delete_all_cookies()
driver.maximize_window()

# Go to specific Pick Em's leaderboard page
driver.get("https://pickem.na.lolesports.com/en-US#leaderboards/list/796749")
WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "#list-container > div > div.rank-table.show-stage-both")))
names_and_scores = get_names_and_scores(driver)
logging.info(names_and_scores)

# Initialize Discord settings
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = "321362348281430018"
client = discord.Client()

@client.event
async def on_ready():
    print("The bot is ready!")
    await client.change_presence(status="Making a bot")

@client.event
async def on_message(message):
    if message.content == "!score":
        channel = client.get_channel(326915348186005505)
        await message.channel.send(generate_scoreboard(names_and_scores))

# Run bot
client.run(TOKEN)

