import discord
from discord.ext import commands 
#from discord.ext.commands  import bot
import os 
from dotenv import load_dotenv
#import music
import asyncio
import yt_dlp as youtube_dl
from yt_dlp import YoutubeDL

import random

load_dotenv()
TOKEN = os.getenv("discord_token")

intents = discord.Intents.all()
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='/',intents=intents) #prefijo

#using Youtube_dl
youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = ''

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]
        filename = data['title'] if stream else ytdl.prepare_filename(data)
        return filename

@bot.command(name='join', help='Tells the bot to join the voice channel')
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send("{} is not connected to a voice channel".format(ctx.message.author.name))
        return
    else:
        channel = ctx.message.author.voice.channel
    await channel.connect()

@bot.command(name='leave', help='To make the bot leave the voice channel')
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_connected():
        await voice_client.disconnect()
    else:
        await ctx.send("The bot is  connected to a voice channel.")

@bot.command(name='play', help='To play song')
async def play(ctx,url):
    try :
        server = ctx.message.guild
        voice_channel = server.voice_client

        async with ctx.typing():
            filename = await YTDLSource.from_url(url, loop=bot.loop)
            voice_channel.play(discord.FFmpegPCMAudio(executable = "ffmpeg.exe", source=filename))
        await ctx.send('**Now playing:** {}'.format(filename))
    except:
        await ctx.send("The bot is not connected to a voice channel.")


@bot.command(name='pause', help='This command pauses the song')
async def pause(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_client.pause()
    else:
        await ctx.send("The bot is not playing anything at the moment.")
    
@bot.command(name='resume', help='Resumes the song')
async def resume(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_paused():
        await voice_client.resume()
    else:
        await ctx.send("The bot was not playing anything before this. Use play_song command")

@bot.command(name='stop', help='Stops the song')
async def stop(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_client.stop()
    else:
        await ctx.send("The bot is not playing anything at the moment.")

@bot.event
async def on_ready():
    print("I am ready")

# List of BoJack Horseman Quotes
quotes = [
    "Because He's So Nice, People Don't Want To Think He's Capable Of Awful Things.",
"When You Look At Someone Through Rose-Colored Glasses, All The Red Flags Just Look Like Flags.",
"The Universe Is A Cruel, Uncaring Voice.",
"Laura! Clear Out The Rest Of My Day!",
"It Gets Easier. Every Day, It Gets A Little Easier. But You Gotta Do It Every Day. That's The Hard Part.",
"I'm Responsible For My Own Happiness? I Can't Even Be Responsible For My Own Breakfast",
"That Voice, The One That Tells You You're Worthless And Stupid And Ugly. It Goes Away, Right?",
"You Turn Yourself Around. That's What It's All About..",
"Before I Leaped, I Should Have Seen The View From Halfway Down.",
"The Rules Are Different For Women.",
"I Feel Like My Life Is Just A Series Of Unrelated Wacky Adventures.",
"He's So Stupid, He Doesn't Realize How Miserable He Should Be. I Envy That.",
"I Need You To Tell Me That I'm A Good Person."
]

@bot.command(name='quote', help='Get a random quote from BoJack Horseman')
async def get_random_quote(ctx):
    random_quote = random.choice(quotes)
    await ctx.send(random_quote)

if __name__ == "__main__":
    bot.run(TOKEN)