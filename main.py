import discord
from discord.ext import commands
from discord.ext.commands import Bot
from bs4 import BeautifulSoup
import requests
import time
import ffmpeg
import youtube_dl
import asyncio

intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix="$", intents=intents)


def search(arg):
    try:
        requests.get("".join(arg))
    except:
        arg = " ".join(arg)
    else:
        arg = "".join(arg)
    with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(f"ytsearch:{arg}", download=False)[
            'entries'][0]
    return info


@client.command(name="play", pass_context=True)
async def play(ctx, url):
    if not ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        FFMPEG_OPTIONS = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        global YDL_OPTIONS
        YDL_OPTIONS = {'format': "bestaudio"}
        vc = ctx.voice_client
        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
            if url.startswith('www') | url.startswith('http'):
                info = ydl.extract_info(url, download=False)
                await ctx.send('Igramo ' + info.get('title'))
                url2 = info['formats'][0]['url']
            else:
                url2 = search(url)['formats'][0]['url']
                await ctx.send('Igramo *' + search(url).get('title') + '*')
            source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
            vc.play(source)


@client.command()
async def pause(ctx):
    await ctx.voice_client.pause()
    await ctx.send("Paused II")


@client.command()
async def resume(ctx):
    await ctx.voice_client.resume()
    await ctx.send("resume")


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
    channelvc = client.get_channel(610548499192479748)
    global vc
    vc = await channelvc.connect()


@client.event
async def on_message(message):  # if message is sent
    if message.author == client.user:
        return
    if message.content.startswith('$rjecnik'):     # call command
        mess = message.content.split()
        if len(mess) == 2:
            if mess[1]:
                print(mess[1])
                await message.channel.send(getDefinition(mess[1]))
        else:
            await message.channel.send('> Komanda: `$rjecnik [rijec]`')

    await client.process_commands(message)

client.run("TOKEN")
