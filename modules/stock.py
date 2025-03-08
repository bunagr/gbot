import discord
from discord.ext import commands
import sqlite3

class Stock(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = self.setup_db()

    def setup_db(self):
        """Set up SQLite database and create the stock table if it doesn't exist."""
        conn = sqlite3.connect("stock.db")
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stock (
                product_name TEXT PRIMARY KEY,
                quantity INTEGER
            )
        """)
        conn.commit()
        return conn

    @commands.command(name="addstock")
    @commands.has_permissions(administrator=True)
    async def add_stock(self, ctx, product_name: str, quantity: int):
        """Add stock to a product."""
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM stock WHERE product_name = ?", (product_name,))
        existing_product = cursor.fetchone()

        if existing_product:
            cursor.execute("""
                UPDATE stock
                SET quantity = quantity + ?
                WHERE product_name = ?
            """, (quantity, product_name))
        else:
            cursor.execute("""
                INSERT INTO stock (product_name, quantity)
                VALUES (?, ?)
            """, (product_name, quantity))

        self.db.commit()
        await ctx.send(f"Added {quantity} {product_name}(s) to the stock.")

    @commands.command(name="removestock")
    @commands.has_permissions(administrator=True)
    async def remove_stock(self, ctx, product_name: str, quantity: int):
        """Remove stock from a product."""
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM stock WHERE product_name = ?", (product_name,))
        existing_product = cursor.fetchone()

        if existing_product and existing_product[1] >= quantity:
            cursor.execute("""
                UPDATE stock
                SET quantity = quantity - ?
                WHERE product_name = ?
            """, (quantity, product_name))
            self.db.commit()
            await ctx.send(f"Removed {quantity} {product_name}(s) from the stock.")
        else:
            await ctx.send(f"Not enough stock of {product_name} to remove {quantity}.")

    @commands.command(name="stock")
    async def view_stock(self, ctx):
        """View all products in stock."""
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM stock")
        stock = cursor.fetchall()

        if not stock:
            await ctx.send("No products in stock.")
        else:
            embed = discord.Embed(title="Current Stock", color=discord.Color.green())
            for product, quantity in stock:
                embed.add_field(name=product, value=f"Quantity: {quantity}", inline=False)
            await ctx.send(embed=embed)

    def cog_unload(self):
        """Close the database connection when the cog is unloaded."""
        self.db.close()

async def setup(bot):
    await bot.add_cog(Stock(bot))
