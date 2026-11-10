import os
import asyncio
import discord
from discord.ext import commands

# 1. SETUP INTENTS
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
bot = commands.Bot(command_prefix="!", intents=intents)

# 2. CONFIGURATION VARIABLES
TOKEN = os.getenv("DISCORD_TOKEN")
VOICE_CHANNEL_ID = 1515034746659274822

keep_alive_task = None

@bot.event
async def on_ready():
    global keep_alive_task
    print(f'Logged in as {bot.user.name} (ID: {bot.user.id})')
    print('------')
    
    channel = bot.get_channel(VOICE_CHANNEL_ID)
    if channel and isinstance(channel, discord.VoiceChannel):
        if keep_alive_task is None or keep_alive_task.done():
            keep_alive_task = asyncio.create_task(stay_in_voice(channel))
    else:
        print("Error: Could not find voice channel. Check your VOICE_CHANNEL_ID.")

async def stay_in_voice(channel):
    """Looping task that ensures the bot stays connected 24/7"""
    while True:
        try:
            vc = discord.utils.get(bot.voice_clients, guild=channel.guild)
            if not vc or not vc.is_connected():
                print(f"Connecting to {channel.name}...")
                await channel.connect(self_deaf=False)
                print(f"Successfully connected to {channel.name} 24/7!")
                
        except Exception as e:
            print(f"Connection error: {e}. Retrying in 10 seconds...")
            
        await asyncio.sleep(10)

@bot.command()
async def join(ctx):
    global keep_alive_task
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        if keep_alive_task is None or keep_alive_task.done():
            keep_alive_task = asyncio.create_task(stay_in_voice(channel))
        await ctx.send(f"Joined **{channel.name}** and staying 24/7.")
    else:
        await ctx.send("You need to be in a voice channel first!")

@bot.command()
async def stop(ctx):
    global keep_alive_task
    if keep_alive_task and not keep_alive_task.done():
        keep_alive_task.cancel()
        keep_alive_task = None
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Disconnected from the voice channel.")

if TOKEN:
    bot.run(TOKEN)
else:
    print("CRITICAL ERROR: DISCORD_TOKEN is missing! Add it in the Environment tab.")
