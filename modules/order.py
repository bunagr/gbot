import discord
from discord.ext import commands
import sqlite3

class Order(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = self.setup_db()

    def setup_db(self):
        """Set up SQLite database and create the orders table if it doesn't exist."""
        conn = sqlite3.connect("orders.db")
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id TEXT PRIMARY KEY,
                product_name TEXT,
                quantity INTEGER,
                total_price REAL,
                status TEXT,
                user TEXT
            )
        """)
        conn.commit()
        return conn

    @commands.command(name="order")
    async def order(self, ctx, product_name: str, quantity: int):
        """Place an order for a product."""
        order_id = f"{ctx.author.id}-{ctx.message.id}"  # Generate a unique order ID based on the user and message ID
        total_price = 100 * quantity  # Assuming each product costs $100, you can modify as needed
        status = "pending"
        user = ctx.author.name
        
        # Insert the order into the SQLite database
        cursor = self.db.cursor()
        cursor.execute("""
            INSERT INTO orders (order_id, product_name, quantity, total_price, status, user)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (order_id, product_name, quantity, total_price, status, user))
        self.db.commit()

        # Send confirmation to the user
        await ctx.send(f"Order placed successfully! Order ID: {order_id} - {product_name} x{quantity} for ${total_price}.")

    @commands.command(name="orderstatus")
    async def order_status(self, ctx, order_id: str):
        """Check the status of an order."""
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,))
        order = cursor.fetchone()

        if order:
            order_id, product_name, quantity, total_price, status, user = order

            # Create embed to display order details
            embed = discord.Embed(title=f"Order Status: {order_id}", color=discord.Color.blue())
            embed.add_field(name="Product", value=product_name, inline=False)
            embed.add_field(name="Quantity", value=quantity, inline=False)
            embed.add_field(name="Total Price", value=f"${total_price}", inline=False)
            embed.add_field(name="Status", value=status, inline=False)
            embed.add_field(name="User", value=user, inline=False)

            await ctx.send(embed=embed)
        else:
            await ctx.send(f"Order with ID {order_id} not found.")

    @commands.command(name="completeorder")
    @commands.has_permissions(administrator=True)
    async def complete_order(self, ctx, order_id: str):
        """Mark an order as completed."""
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,))
        order = cursor.fetchone()

        if order:
            cursor.execute("UPDATE orders SET status = ? WHERE order_id = ?", ("completed", order_id))
            self.db.commit()
            await ctx.send(f"Order {order_id} has been marked as completed.")
        else:
            await ctx.send(f"Order with ID {order_id} not found.")

    @commands.command(name="cancelorder")
    @commands.has_permissions(administrator=True)
    async def cancel_order(self, ctx, order_id: str):
        """Cancel an order."""
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,))
        order = cursor.fetchone()

        if order:
            cursor.execute("UPDATE orders SET status = ? WHERE order_id = ?", ("canceled", order_id))
            self.db.commit()
            await ctx.send(f"Order {order_id} has been canceled.")
        else:
            await ctx.send(f"Order with ID {order_id} not found.")

    def cog_unload(self):
        """Close the database connection when the cog is unloaded."""
        self.db.close()

async def setup(bot):
    await bot.add_cog(Order(bot))
