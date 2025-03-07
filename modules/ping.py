from discord.ext import commands

class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ping")  # Ensure the command is named correctly
    async def ping(self, ctx):
        await ctx.send("Pong!")

async def setup(bot):  # Must be async for new discord.py versions
    await bot.add_cog(Ping(bot))
