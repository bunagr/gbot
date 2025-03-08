import discord
from discord.ext import commands
import sqlite3
from datetime import datetime

class ClockInSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = self.setup_db()

    def setup_db(self):
        """Set up SQLite database and create the clock_in table if it doesn't exist."""
        conn = sqlite3.connect("clock_in_out.db")
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clock_in_out (
                user_id INTEGER PRIMARY KEY,
                clock_in_time TEXT,
                clock_out_time TEXT,
                total_hours REAL
            )
        """)
        conn.commit()
        return conn

    @commands.command(name="clockin")
    async def clock_in(self, ctx):
        """Clock in the staff member."""
        user_id = ctx.author.id
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM clock_in_out WHERE user_id = ?", (user_id,))
        existing_entry = cursor.fetchone()

        if existing_entry and existing_entry[2] is None: 
            embed = discord.Embed(
                title="Clock In Error",
                description="You are already clocked in. Please clock out first.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
        else:
            clock_in_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            if existing_entry:
                # Update the existing clock-in time if there's a previous record
                cursor.execute("""
                    UPDATE clock_in_out
                    SET clock_in_time = ?, clock_out_time = NULL, total_hours = 0
                    WHERE user_id = ?
                """, (clock_in_time, user_id))
            else:
                # Insert a new record for first-time clocking in
                cursor.execute("""
                    INSERT INTO clock_in_out (user_id, clock_in_time, clock_out_time, total_hours)
                    VALUES (?, ?, NULL, 0)
                """, (user_id, clock_in_time))
            self.db.commit()

            embed = discord.Embed(
                title="Clock In Successful",
                description=f"{ctx.author.name}, you have clocked in at {clock_in_time}.",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)

    @commands.command(name="clockout")
    async def clock_out(self, ctx):
        """Clock out the staff member and calculate the total hours worked."""
        user_id = ctx.author.id
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM clock_in_out WHERE user_id = ?", (user_id,))
        existing_entry = cursor.fetchone()

        if existing_entry and existing_entry[2] is None:  # Check if clocked in but not clocked out
            clock_in_time = datetime.strptime(existing_entry[1], '%Y-%m-%d %H:%M:%S')
            clock_out_time = datetime.now()
            total_worked_time = (clock_out_time - clock_in_time).total_seconds() / 3600  # in hours

            cursor.execute("""
                UPDATE clock_in_out
                SET clock_out_time = ?, total_hours = ?
                WHERE user_id = ?
            """, (clock_out_time.strftime('%Y-%m-%d %H:%M:%S'), total_worked_time, user_id))
            self.db.commit()

            embed = discord.Embed(
                title="Clock Out Successful",
                description=f"{ctx.author.name}, you have clocked out at {clock_out_time.strftime('%Y-%m-%d %H:%M:%S')}.\nTotal worked time: {total_worked_time:.2f} hours.",
                color=discord.Color.blue()
            )
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title="Clock Out Error",
                description="You are not clocked in or have already clocked out.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    @commands.command(name="worktime")
    async def work_time(self, ctx):
        """Show the total hours worked for the day."""
        user_id = ctx.author.id
        cursor = self.db.cursor()
        cursor.execute("SELECT total_hours FROM clock_in_out WHERE user_id = ?", (user_id,))
        existing_entry = cursor.fetchone()

        if existing_entry and existing_entry[0] > 0:
            embed = discord.Embed(
                title="Work Time",
                description=f"{ctx.author.name}, you have worked a total of {existing_entry[0]:.2f} hours today.",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title="Work Time Error",
                description=f"{ctx.author.name}, you have not clocked out yet today or have no recorded hours.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    @commands.command(name="clockstatus")
    async def clock_status(self, ctx):
        """Show the current clock-in status of the staff member."""
        user_id = ctx.author.id
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM clock_in_out WHERE user_id = ?", (user_id,))
        existing_entry = cursor.fetchone()

        if existing_entry:
            clock_in_time = existing_entry[1]
            clock_out_time = existing_entry[2]
            total_hours = existing_entry[3]

            if clock_out_time is None:
                status = "You are currently clocked in."
            else:
                status = f"You clocked out at {clock_out_time}. Total worked time: {total_hours:.2f} hours."

            embed = discord.Embed(
                title="Clock Status",
                description=f"{ctx.author.name}, {status}",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title="Clock Status Error",
                description="You haven't clocked in yet.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    def cog_unload(self):
        """Close the database connection when the cog is unloaded."""
        self.db.close()

async def setup(bot):
    await bot.add_cog(ClockInSystem(bot))
