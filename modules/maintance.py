import discord
from discord.ext import commands

class Maintenance(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="maintenance")
    async def maintenance(self, ctx, mode: str = None):
        """Toggle maintenance mode (only for allowed user)."""
        if ctx.author.id != 1255309054167875637: 
            return await ctx.send("⛔ You don't have permission to change maintenance mode.")

        if mode is None:
            return await ctx.send("⚠️ Usage: `!maintenance on` or `!maintenance off`")

        if mode.lower() == "on":
            self.bot.maintenance_mode = True
            await ctx.send("🚧 **Maintenance mode enabled!**")
        elif mode.lower() == "off":
            self.bot.maintenance_mode = False
            await ctx.send("✅ **Maintenance mode disabled!**")
        else:
            await ctx.send("⚠️ Invalid option. Use `!maintenance on` or `!maintenance off`.")

async def setup(bot):
    await bot.add_cog(Maintenance(bot))
