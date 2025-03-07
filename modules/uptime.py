import discord
from discord.ext import commands
import time
from datetime import timedelta

class Uptime(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='uptime')
    async def uptime(self, ctx):
        uptime_seconds = time.time() - self.bot.start_time
        uptime_str = str(timedelta(seconds=int(uptime_seconds)))

        embed = discord.Embed(title="Bot Uptime", description=f"🟢 **{uptime_str}**", color=discord.Color.green())
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Uptime(bot))
