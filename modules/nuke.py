import discord
from discord.ext import commands

class ChannelManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # List of allowed user IDs that can use the command
        self.allowed_users = [1255309054167875637, 1255309054167875637]

    @commands.command(name="nuke")
    async def reset_channel(self, ctx, channel: discord.TextChannel):
        """Deletes and recreates the specified channel."""
        
        # Check if the user is allowed to use this command
        if ctx.author.id not in self.allowed_users:
            embed = discord.Embed(
                title="Permission Denied",
                description="You do not have permission to use this command.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        try:
            # Get the channel name and category (if any)
            channel_name = channel.name
            category = channel.category

            # Ensure the bot has Manage Channels permission
            if not channel.permissions_for(ctx.guild.me).manage_channels:
                await ctx.send("I do not have permission to manage channels.")
                return

            # Delete the channel
            await channel.delete()

            # Recreate the channel in the same category
            if category:
                new_channel = await category.create_text_channel(channel_name)
            else:
                # If there's no category, create the channel in the default category
                new_channel = await ctx.guild.create_text_channel(channel_name)

            # Send a confirmation message
            embed = discord.Embed(
                title="Channel Reset",
                description=f"The channel {channel.mention} has been deleted and recreated as {new_channel.mention}.",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)

        except discord.Forbidden:
            await ctx.send("I do not have permission to delete or create channels.")
        except discord.HTTPException as e:
            await ctx.send(f"An error occurred: {e}")
        except Exception as e:
            await ctx.send(f"Something went wrong: {e}")

async def setup(bot):
    await bot.add_cog(ChannelManager(bot))
