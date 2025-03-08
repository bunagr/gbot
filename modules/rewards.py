import discord
from discord.ext import commands
import sqlite3
import json
import os

class Rewards(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = self.setup_db()
        self.admin_id = 1255309054167875637  # Replace with the admin's user ID
        self.codes_file = "codes.json"
        self.load_codes()
        self.claimed_list_channel_id = 1347967052752617614  # Replace with the ID of the channel where you want to display the claim list

    def setup_db(self):
        """Set up SQLite database and create the rewards table if it doesn't exist."""
        conn = sqlite3.connect("rewards.db")
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rewards (
                user_id INTEGER PRIMARY KEY,
                points INTEGER,
                extra_slots INTEGER
            )
        """)
        conn.commit()
        return conn

    def load_codes(self):
        """Load available, claimed, and rewarded codes from the JSON file."""
        if os.path.exists(self.codes_file):
            with open(self.codes_file, "r") as file:
                self.codes = json.load(file)
        else:
            self.codes = {"available": [], "claimed": [], "rewarded": []}

    def save_codes(self):
        """Save available, claimed, and rewarded codes back to the JSON file."""
        with open(self.codes_file, "w") as file:
            json.dump(self.codes, file, indent=4)

    @commands.command(name="addreward")
    async def add_reward(self, ctx, member: discord.Member, points: int):
        """Allow an admin to add reward points to a user."""
        if ctx.author.id != self.admin_id:
            embed = discord.Embed(
                title="Permission Denied",
                description="You do not have permission to add reward points.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        cursor = self.db.cursor()
        cursor.execute("SELECT points, extra_slots FROM rewards WHERE user_id = ?", (member.id,))
        result = cursor.fetchone()

        if result:
            new_points = result[0] + points
            cursor.execute("UPDATE rewards SET points = ? WHERE user_id = ?", (new_points, member.id))
        else:
            cursor.execute("INSERT INTO rewards (user_id, points, extra_slots) VALUES (?, ?, ?)", (member.id, points, 0))
        
        self.db.commit()

        embed = discord.Embed(
            title="Reward Points Added",
            description=f"{points} reward points have been added to {member.mention}.",
            color=discord.Color.green()
        )
        embed.add_field(name="New Total Points", value=str(new_points if result else points), inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="removereward")
    async def remove_reward(self, ctx, member: discord.Member, points: int):
        """Allow an admin to remove reward points from a user."""
        if ctx.author.id != self.admin_id:
            embed = discord.Embed(
                title="Permission Denied",
                description="You do not have permission to remove reward points.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        cursor = self.db.cursor()
        cursor.execute("SELECT points FROM rewards WHERE user_id = ?", (member.id,))
        result = cursor.fetchone()

        if result:
            current_points = result[0]
            if current_points >= points:
                new_points = current_points - points
                cursor.execute("UPDATE rewards SET points = ? WHERE user_id = ?", (new_points, member.id))
                embed = discord.Embed(
                    title="Reward Points Removed",
                    description=f"{points} reward points have been removed from {member.mention}.",
                    color=discord.Color.red()
                )
                embed.add_field(name="New Total Points", value=str(new_points), inline=False)
            else:
                embed = discord.Embed(
                    title="Insufficient Points",
                    description=f"{member.mention} does not have enough points to remove {points} points.",
                    color=discord.Color.orange()
                )
        else:
            embed = discord.Embed(
                title="No Reward Points",
                description=f"{member.mention} has no reward points to remove.",
                color=discord.Color.orange()
            )
        
        self.db.commit()
        await ctx.send(embed=embed)

    @commands.command(name="rew")
    async def view_rewards(self, ctx):
        """View the current reward points of the user."""
        cursor = self.db.cursor()
        cursor.execute("SELECT points FROM rewards WHERE user_id = ?", (ctx.author.id,))
        result = cursor.fetchone()

        if result:
            embed = discord.Embed(
                title=f"{ctx.author.display_name}'s Reward Points",
                description=f"You currently have {result[0]} reward points.",
                color=discord.Color.blue()
            )
        else:
            embed = discord.Embed(
                title="No Reward Points",
                description="You do not have any reward points yet.",
                color=discord.Color.orange()
            )

        await ctx.send(embed=embed)

    @commands.command(name="cashout")
    async def cashout(self, ctx):
        """Allow users to cash out their points for a code."""
        cursor = self.db.cursor()
        cursor.execute("SELECT points FROM rewards WHERE user_id = ?", (ctx.author.id,))
        result = cursor.fetchone()

        if result and result[0] >= 100:  # Set the cashout requirement (e.g., 100 points)
            if self.codes["available"]:
                # Provide a code and remove it from available codes
                code_info = self.codes["available"].pop(0)
                code = code_info["code"]
                self.codes["claimed"].append(code_info)
                self.save_codes()

                # Subtract 100 points
                new_points = result[0] - 100
                cursor.execute("UPDATE rewards SET points = ? WHERE user_id = ?", (new_points, ctx.author.id))
                self.db.commit()

                try:
                    # Send DM with the code
                    dm_embed = discord.Embed(
                        title="Cashout Successful",
                        description=f"You've cashed out 100 points for the code: `{code}`.",
                        color=discord.Color.green()
                    )
                    await ctx.author.send(embed=dm_embed)
                except discord.errors.Forbidden:
                    # Handle case where the user has DMs disabled
                    await ctx.send(f"Could not send you the code in DM, {ctx.author.mention}. Please enable DMs to receive the code.")
                
                # Inform the user in the public channel that the cashout was successful
                embed = discord.Embed(
                    title="Cashout Successful",
                    description="The code has been sent to your DMs.",
                    color=discord.Color.green()
                )
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(
                    title="No Available Codes",
                    description="There are no available codes left to cash out. Please check back later.",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title="Insufficient Points",
                description="You need at least 100 reward points to cash out for a code.",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)

    @commands.command(name="claim")
    async def claim(self, ctx, code: str):
        """Allow users to claim a code."""
        code_info = None
        for code_data in self.codes["claimed"]:
            if code_data["code"] == code:
                code_info = code_data
                break

        if code_info:
            # Add the user to the claimed list
            claimants_channel = self.bot.get_channel(self.claimed_list_channel_id)
            if claimants_channel:
                await claimants_channel.send(f"{ctx.author.mention} has claimed the code `{code}`. And has have been rewarded {code_info['reward']['points']} points and {code_info['reward']['extra_slots']} extra slots. ")

            # Move the code to rewarded list
            self.codes["claimed"].remove(code_info)
            self.codes["rewarded"].append(code_info)
            self.save_codes()

            # Grant the reward
            cursor = self.db.cursor()
            cursor.execute("SELECT points, extra_slots FROM rewards WHERE user_id = ?", (ctx.author.id,))
            result = cursor.fetchone()

            if result:
                current_points, current_slots = result
                # Add the reward points and extra slots to the user's account
                new_points = current_points + code_info["reward"]["points"]
                new_slots = current_slots + code_info["reward"]["extra_slots"]
                cursor.execute("UPDATE rewards SET points = ?, extra_slots = ? WHERE user_id = ?", (new_points, new_slots, ctx.author.id))
                self.db.commit()

            embed = discord.Embed(
                title="Code Claimed and Rewarded",
                description=f"Congratulations, {ctx.author.mention}! You have successfully claimed and received the code: `{code}`. You have been rewarded {code_info['reward']['points']} points and {code_info['reward']['extra_slots']} extra slots.",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)

        else:
            embed = discord.Embed(
                title="Invalid Code",
                description="The code you entered is not valid or has already been claimed by another user.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    def cog_unload(self):
        """Close the database connection when the cog is unloaded."""
        self.db.close()

async def setup(bot):
    await bot.add_cog(Rewards(bot))
