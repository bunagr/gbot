import discord
from discord.ext import commands
import sys
import os
import time

class Reboot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.allowed_user_id = 1255309054167875637  # Replace with your Discord ID
        self.reboot_channel_name = "status"  # Replace with the name of your channel

    @commands.command(name="reboot")
    async def reboot(self, ctx):
        """Reboots the bot."""
        if ctx.author.id != self.allowed_user_id:
            embed = discord.Embed(
                title="Permission Denied",
                description="You do not have permission to reboot the bot.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        # Find the channel by name
        channel = discord.utils.get(ctx.guild.text_channels, name=self.reboot_channel_name)
        if not channel:
            await ctx.send("Could not find the specified channel for the reboot message.")
            return

        # Send reboot message to the specified channel as plain text with a reboot emoji
        await channel.send("🔄 The bot is restarting...")

        # Send a confirmation message to the current channel
        confirmation_embed = discord.Embed(
            title="Bot Reboot",
            description="The bot is restarting...",
            color=discord.Color.orange()
        )
        await ctx.send(embed=confirmation_embed)

        # Wait for the message to be sent
        time.sleep(2)

        # Reboot the bot by re-running the script
        os.execv(sys.executable, ['python'] + sys.argv)  # This will restart the bot process

async def setup(bot):
    await bot.add_cog(Reboot(bot))
