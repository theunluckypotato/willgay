import os
import asyncio
import discord
from discord.ext import commands
import yt_dlp

# 1. SETUP LOGISTICS & INTENTS
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True  # Required to track, join, and stay inside voice channels
bot = commands.Bot(command_prefix="!", intents=intents)

# 2. CONFIGURATION VARIABLES
TOKEN = "MTU2OTc3NTAwMjc4ODU2NTAyMw.G-sywW.kVOx-yi7rgj2hzqhEQn86Fsy6A4uoO8grBuaJM"
VOICE_CHANNEL_ID = 1515034746659274822  

# 24/7 Lofi YouTube Link
STREAM_URL = "https://www.youtube.com/watch?v=qH3fETPsqXU" 

YTDL_OPTIONS = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'extract_flat': False
}

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn -bufsize 2000k'
}

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} (ID: {bot.user.id})')
    print('------')
    
    channel = bot.get_channel(VOICE_CHANNEL_ID)
    if channel and isinstance(channel, discord.VoiceChannel):
        asyncio.create_task(keep_alive_playback(channel))
    else:
        print("Error: Could not find voice channel. Check your VOICE_CHANNEL_ID.")

async def keep_alive_playback(channel):
    """Looping task that keeps the bot connected and playing 24/7"""
    ytdl = yt_dlp.YoutubeDL(YTDL_OPTIONS)
    
    while True:
        try:
            vc = discord.utils.get(bot.voice_clients, guild=channel.guild)
            if not vc:
                vc = await channel.connect()
            
            if not vc.is_playing():
                print(f"Extracting streaming audio from YouTube source...")
                loop = asyncio.get_event_loop()
                data = await loop.run_in_executor(None, lambda: ytdl.extract_info(STREAM_URL, download=False))
                
                url = data['url']
                print(f"Starting 24/7 playback stream in {channel.name}...")
                
                source = discord.FFmpegPCMAudio(url, **FFMPEG_OPTIONS)
                vc.play(source)
                
        except Exception as e:
            print(f"Playback error encountered: {e}. Reconnecting in 10 seconds...")
            
        await asyncio.sleep(10)

@bot.command()
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
        asyncio.create_task(keep_alive_playback(channel))

@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()

bot.run(os.getenv("DISCORD_TOKEN"))

