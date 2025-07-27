# discord_bot.py
import asyncio
from typing import Optional

import discord
from discord.ext import commands
from discord.commands import SlashCommandGroup, Option

# ---- build the bot (no network I/O here) ----
def build_bot(searcher, guild_id: Optional[int] = None) -> commands.Bot:
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix="!", intents=intents)

    # Events
    @bot.event
    async def on_ready():
        await bot.wait_until_ready()
        if guild_id:
            await bot.sync_commands(guild_ids=[guild_id])  # instant for dev
        else:
            await bot.sync_commands()                      # global (slow)
        print(f"{bot.user} connected. In {len(bot.guilds)} guild(s). Slash commands synced.")

    @bot.event
    async def on_application_command_error(ctx, error):
        # Surface errors so you don't just see "application didn't respond"
        try:
            await ctx.respond(f"⚠️ Error: {error}", ephemeral=True)
        except Exception:
            pass
        # Also print to console for stack traces
        import traceback
        traceback.print_exception(type(error), error, error.__traceback__)

    # Example test command
    @bot.slash_command(description="Quick ping", guild_ids=[guild_id] if guild_id else None)
    async def ping(ctx: discord.ApplicationContext):
        await ctx.respond("pong", ephemeral=True)

    # /alerts group
    alerts = SlashCommandGroup(
        "alerts",
        "Manage alerts",
        guild_ids=[guild_id] if guild_id else None
    )
    bot.add_application_command(alerts)

    @alerts.command(name="list", description="List current search terms")
    async def list_(ctx: discord.ApplicationContext):
        terms = searcher.get_search_terms()
        if not terms:
            await ctx.respond("No search terms yet.", ephemeral=True)
            return
        await ctx.respond("Current search terms: " + ", ".join(terms), ephemeral=True)

    # add /alerts add|remove later…

    @alerts.command(name="add", description="Add to current search terms")
    async def list_(ctx: discord.ApplicationContext, term: Option(str, "Term to track")):
        searcher.add_search_term(term)
        await ctx.respond("Search term: \"" + term + "\" added to the list.", ephemeral=True)

    @alerts.command(name="remove", description="Remove current search terms")
    async def list_(ctx: discord.ApplicationContext, term: Option(str, "Term to track")):
        searcher.remove_search_term(term)
        await ctx.respond("Search term: \"" + term + "\" removed from the list.", ephemeral=True)

    @alerts.command(name="rescan", description="Rescan all items in RSS feed with current search terms")
    async def list_(ctx: discord.ApplicationContext):
        terms = searcher.get_search_terms()
        await ctx.respond("Searching all items for terms: " + ", ".join(terms), ephemeral=True)
        matchedItems = searcher.find_matches()
        for each in matchedItems:
            item_id = each["id"]
            url = each["url"]
            term = each["terms"]
            term_str = ", ".join(term) if isinstance(term, (list, tuple, set)) else str(term)
            await ctx.followup.send(f"Found match for {term_str}: {url}" , ephemeral=True)

    return bot


# ---- run the bot (blocking) ----
def run_bot(searcher=None, guild_id: Optional[int] = None):
    """
    Start the Discord bot. Safe to call from a background thread.
    Creates its own asyncio event loop (needed on Python 3.11+ in threads).
    """
    from config.settings import DISCORD_TOKEN
    if searcher is None:
        from scraper.search_engine import FederalRegisterSearcher
        searcher = FederalRegisterSearcher()

    # Create and set an event loop for THIS thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    bot = build_bot(searcher, guild_id)

    async def _runner():
        try:
            await bot.start(DISCORD_TOKEN)
        finally:
            await bot.close()

    try:
        loop.run_until_complete(_runner())
    finally:
        loop.close()


# Allow `python discord_bot.py` standalone
if __name__ == "__main__":
    from scraper.search_engine import FederalRegisterSearcher
    from config.settings import GUILD_ID  # optional; fine if you keep it there

    searcher = FederalRegisterSearcher()
    run_bot(searcher, GUILD_ID)
