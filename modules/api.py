import discord
from discord.ext import commands, tasks
import requests
import asyncio

class Api(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.allowed_user_id = 1255309054167875637  
        self.channel_id = 1347534543237681246  
        self.api_url = "https://google.com"  

        # Initialize the task to update the status embed every 5 seconds
        self.api_status.start()

    @tasks.loop(seconds=5)  # This task will run every 5 seconds
    async def api_status(self):
        # Fetch the status of the API
        try:
            response = requests.get(self.api_url)
            status_code = response.status_code
            status_message = "API is up!" if status_code == 200 else f"API returned status code {status_code}"
        except requests.RequestException:
            status_message = "Failed to reach the API."

        # Get the channel by ID
        channel = self.bot.get_channel(self.channel_id)
        if channel:
            # Create and send an embed with the updated API status
            embed = discord.Embed(
                title="API Status",
                description=status_message,
                color=discord.Color.green() if status_code == 200 else discord.Color.red()
            )
            embed.set_footer(text="Updating every 5 seconds...")
            # Send the embed or update the last message
            if hasattr(self, 'last_message'):
                await self.last_message.edit(embed=embed)
            else:
                self.last_message = await channel.send(embed=embed)

    @commands.command(name="apistatus")
    async def apistat(self, ctx):
        """Manually trigger the API status command."""
        try:
            response = requests.get(self.api_url)
            status_code = response.status_code
            status_message = "API is up!" if status_code == 200 else f"API returned status code {status_code}"
        except requests.RequestException:
            status_message = "Failed to reach the API."

        embed = discord.Embed(
            title="API Status",
            description=status_message,
            color=discord.Color.green() if status_code == 200 else discord.Color.red()
        )
        embed.set_footer(text="Manual status check.")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Api(bot))
