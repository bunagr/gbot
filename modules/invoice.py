import discord
from discord.ext import commands
import sqlite3
import uuid
from datetime import datetime

class Invoice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = self.setup_db()

    def setup_db(self):
        """Set up SQLite database and create the invoices table if it doesn't exist."""
        conn = sqlite3.connect("invoices.db")
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS invoices (
                invoice_id TEXT PRIMARY KEY,
                client_name TEXT,
                product_name TEXT,
                quantity INTEGER,
                total_price REAL,
                date TEXT
            )
        """)
        conn.commit()
        return conn

    @commands.command(name="createinvoice")
    @commands.has_permissions(administrator=True)
    async def create_invoice(self, ctx, client_name: str, product_name: str, quantity: int):
        """Create an invoice with a unique ID."""
        # Check if the product exists in stock
        if product_name in self.bot.get_cog("Stock").stock_data and self.bot.get_cog("Stock").stock_data[product_name] >= quantity:
            # Generate a unique invoice ID
            invoice_id = str(uuid.uuid4())
            total_price = 100 * quantity  # Price per product (hardcoded for simplicity)

            # Insert the invoice into the SQLite database
            cursor = self.db.cursor()
            cursor.execute("""
                INSERT INTO invoices (invoice_id, client_name, product_name, quantity, total_price, date)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (invoice_id, client_name, product_name, quantity, total_price, str(datetime.now())))
            self.db.commit()

            # Update stock
            self.bot.get_cog("Stock").stock_data[product_name] -= quantity  # Deduct stock
            self.bot.get_cog("Stock").save_stock_data()  # Save updated stock

            # Send confirmation to the user
            await ctx.send(f"Invoice created successfully! Invoice ID: {invoice_id}")
        else:
            await ctx.send(f"Not enough stock for {product_name}.")

    @commands.command(name="viewinvoice")
    async def view_invoice(self, ctx, invoice_id: str):
        """View an invoice by ID."""
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM invoices WHERE invoice_id = ?", (invoice_id,))
        invoice = cursor.fetchone()

        if invoice:
            invoice_id, client_name, product_name, quantity, total_price, date = invoice

            # Create embed to display invoice details
            embed = discord.Embed(title=f"Invoice ID: {invoice_id}", color=discord.Color.blue())
            embed.add_field(name="Client", value=client_name, inline=False)
            embed.add_field(name="Product", value=product_name, inline=False)
            embed.add_field(name="Quantity", value=quantity, inline=False)
            embed.add_field(name="Total Price", value=f"${total_price}", inline=False)
            embed.add_field(name="Date", value=date, inline=False)

            await ctx.send(embed=embed)
        else:
            await ctx.send(f"Invoice with ID {invoice_id} not found.")

    @commands.command(name="invoicecount")
    async def invoice_count(self, ctx):
        """Displays the total number of invoices."""
        cursor = self.db.cursor()
        cursor.execute("SELECT COUNT(*) FROM invoices")
        total_invoices = cursor.fetchone()[0]  # Get the count of invoices
        await ctx.send(f"Total number of invoices: {total_invoices}")

    def cog_unload(self):
        """Close the database connection when the cog is unloaded."""
        self.db.close()

async def setup(bot):
    await bot.add_cog(Invoice(bot))
