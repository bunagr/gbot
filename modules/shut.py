import discord
from discord.ext import commands
import sys

class Shutdown(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.allowed_user_id = 1255309054167875637 
        
    @commands.command(name="shut")
    async def shut(self, ctx):
        """Shuts down the bot."""
        if ctx.author.id != self.allowed_user_id:
            embed = discord.Embed(
                title="Permission Denied",
                description="You do not have permission to shut down the bot.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        embed = discord.Embed(
            title="Bot Shutdown",
            description="The bot is shutting down...",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

        # Terminate the bot process
        sys.exit()  # This will stop the bot process

async def setup(bot):
    await bot.add_cog(Shutdown(bot))
