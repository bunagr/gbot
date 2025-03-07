import discord
from discord.ext import commands
import os
import toml
import asyncio
import time

# Load config
config = toml.load("config.toml")
TOKEN = config["bot"]["token"]
PREFIX = config["bot"]["prefix"]

# Set allowed user (replace with your Discord user ID)
allowedUserID = 1255309054167875637  # CHANGE THIS TO YOUR DISCORD ID

# Initialize bot
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

# Track bot start time & maintenance mode
bot.start_time = time.time()
bot.maintenance_mode = False  # Default: OFF

# Function to load commands
async def load_commands():
    for filename in os.listdir("./modules"):
        if filename.endswith(".py"):
            ext = f"modules.{filename[:-3]}"
            try:
                await bot.load_extension(ext)
                print(f"✅ Loaded {filename}")
            except commands.ExtensionAlreadyLoaded:
                await bot.reload_extension(ext)
                print(f"🔄 Reloaded {filename}")
            except Exception as e:
                print(f"❌ Failed to load {filename}: {e}")

# Check maintenance mode before processing commands
@bot.check
async def maintenance_check(ctx):
    if bot.maintenance_mode and ctx.author.id != allowedUserID:
        await ctx.send("🚧 The bot is currently in maintenance mode.")
        return False
    return True

# Load commands on startup
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    print(f"🔎 Registered commands: {[cmd.name for cmd in bot.commands]}")  # Debugging

# Reload command
@bot.command()
@commands.has_permissions(administrator=True)
async def reload(ctx):
    await load_commands()
    await ctx.send("✅ Commands reloaded!")

# Async bot startup
async def main():
    async with bot:
        await load_commands()
        await bot.start(TOKEN)

asyncio.run(main())
