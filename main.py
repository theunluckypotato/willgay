import os
import asyncio
import discord
from discord.ext import commands
import yt_dlp

# 1. SETUP INTENTS
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
bot = commands.Bot(command_prefix="!", intents=intents)

# 2. CONFIGURATION VARIABLES
TOKEN = os.getenv("DISCORD_TOKEN")
VOICE_CHANNEL_ID = 1515034746659274822
STREAM_URL = "https://youtube.com"

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

# Prevents multiple audio loops from running at the same time
playback_task = None

@bot.event
async def on_ready():
    global playback_task
    print(f'Logged in as {bot.user.name} (ID: {bot.user.id})')
    print('------')
    
    channel = bot.get_channel(VOICE_CHANNEL_ID)
    if channel and isinstance(channel, discord.VoiceChannel):
        if playback_task is None or playback_task.done():
            playback_task = asyncio.create_task(keep_alive_playback(channel))
    else:
        print("Error: Could not find voice channel. Check your VOICE_CHANNEL_ID.")

async def keep_alive_playback(channel):
    """Looping task that keeps the bot connected and playing 24/7"""
    ytdl = yt_dlp.YoutubeDL(YTDL_OPTIONS)
    
    while True:
        try:
            vc = discord.utils.get(bot.voice_clients, guild=channel.guild)
            if not vc or not vc.is_connected():
                vc = await channel.connect(self_deaf=False)
            
            if not vc.is_playing() and not vc.is_paused():
                print("Extracting streaming audio from YouTube source...")
                loop = asyncio.get_running_loop()
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
    global playback_task
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        if playback_task is None or playback_task.done():
            playback_task = asyncio.create_task(keep_alive_playback(channel))
        await ctx.send(f"Joined **{channel.name}** and started 24/7 radio.")
    else:
        await ctx.send("You need to be in a voice channel first!")

@bot.command()
async def stop(ctx):
    global playback_task
    if playback_task and not playback_task.done():
        playback_task.cancel()
        playback_task = None
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Disconnected and stopped the radio.")

if TOKEN:
    bot.run(TOKEN)
else:
    print("CRITICAL ERROR: DISCORD_TOKEN is missing! Add it in the Environment tab.")
