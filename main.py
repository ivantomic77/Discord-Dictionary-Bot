import discord
from discord.ext import commands
from bs4 import BeautifulSoup
import requests

client = discord.Client()   # discord client

topic = ''


def getDefinition(topic):   # Web scraping word meaning
    meaning = ''
    # list order number
    index = 1

    html_text = requests.get('https://vukajlija.com/' + topic).text
    soup = BeautifulSoup(html_text, 'lxml')

    # if definition doesn't exist
    if soup.find('head').find('title').text == 'Strana ne postoji (404)':
        # change source
        html_text = requests.get(
            'https://vukajlija.com/pretraga/izraz?q=' + topic).text
        soup = BeautifulSoup(html_text, 'lxml')
        result = soup.find_all('div', class_='copy')

        # if definition doesn't exist here either
        if soup.find('div', class_='post-container').find('h2').text == 'Neverovatno!':
            meaning = '```diff\n- Definicija ne postoji\n```'
            return meaning

        for definition in result:
            meaning = meaning + '\n' + \
                '**{}.** '.format(index) + '\n```' + \
                definition.find('p').text + '```'
            index += 1
            if index == 4:
                break
        return meaning

    result = soup.find_all('div', class_='copy')

    for definition in result:
        meaning = meaning + '\n' + \
            '**{}.** '.format(index) + '\n```' + \
            definition.find('p').text + '```'
        index += 1
        if index == 4:
            break
    return meaning


@client.event
async def on_ready():   # bot logged in
    print('we loged in as {0.user}'.format(client))
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="you."))


@client.event
async def on_message(message):  # if message is sent
    if message.author == client.user:
        return
    if message.content.startswith('$rjecnik'):     # call command
        mess = message.content.split()
        if len(mess) == 2:
            if mess[1]:
                await message.channel.send(getDefinition(mess[1]))
        else:
            await message.channel.send('> Komanda: `$rjecnik [rijec]`')

client.run("OTkyNzM0OTU5OTEzNjg1MDQz.G-YaZy.vP7LSCfZN7qG7JccdC51GSDBjxyHEb9N1EtkPM")
