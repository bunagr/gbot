import discord
from discord.ext import commands

class Announcement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="announcement")
    @commands.has_permissions(administrator=True)  
    async def announcement(self, ctx, channel: discord.TextChannel, *, message: str):
        """Send an announcement to a specific channel as an embed."""
        
        embed = discord.Embed(
            title="Announcement",
            description=message,
            color=discord.Color.blue()
        )
        
        embed.set_footer(text=f"Announcement by {ctx.author.name}", icon_url=ctx.author.avatar.url)
        
        await channel.send(embed=embed)
        await ctx.send(f"Announcement sent to {channel.mention}!")

    @announcement.error
    async def announcement_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("⛔ You don't have permission to use this command.")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("⚠️ Invalid channel or message format. Please check your command syntax.")

async def setup(bot):
    await bot.add_cog(Announcement(bot))
