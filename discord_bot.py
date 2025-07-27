# discord_bot.py
import asyncio
from typing import Optional
import time
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
        await ctx.defer(ephemeral=True)
        terms = searcher.get_search_terms()
        if not terms:
            await ctx.followup.send("No search terms yet.", ephemeral=True)
            return
        await ctx.followup.send("Current search terms: " + ", ".join(terms), ephemeral=True)

    # add /alerts add|remove later…

    @alerts.command(name="add", description="Add a search term")
    async def add_(ctx, term: str):
        await ctx.defer(ephemeral=True)  # instant ACK so no timeout
        ok = searcher.add_search_term(term)  # synchronous; quick
        msg = f'Added "{term}".' if ok else f'"{term}" was already tracked.'
        await ctx.followup.send(msg, ephemeral=True)

    @alerts.command(name="remove", description="Remove current search terms")
    async def remove_(ctx: discord.ApplicationContext, term: Option(str, "Term to track")):
        await ctx.defer(ephemeral=True)
        searcher.remove_search_term(term)
        await ctx.followup.send("Search term: \"" + term + "\" removed from the list.", ephemeral=True)

    @alerts.command(name="rescan", description="Rescan all items in RSS feed with current search terms")
    async def rescan_(ctx: discord.ApplicationContext):
        await ctx.defer(ephemeral=True)  # show the typing/loader
        terms = searcher.get_search_terms()
        msg = await ctx.followup.send(f"⏳ Scanning all items for: {', '.join(terms)}",ephemeral=True)
        stop = asyncio.Event()

        async def spinner():
            frames = ["⏳", "🔎", "⌛"]
            i = 0
            while not stop.is_set():
                await msg.edit(content=f"{frames[i % len(frames)]} Scanning all items for: {', '.join(terms)}")
                i += 1
                # gentle on rate limits
                try:
                    await asyncio.wait_for(stop.wait(), timeout=1.5)
                except asyncio.TimeoutError:
                    pass
        spin_task = asyncio.create_task(spinner())

        try:
            # run CPU/network heavy work off the event loop
            matches = await asyncio.to_thread(searcher.find_matches)
        except Exception as e:
            stop.set();
            await spin_task
            await msg.edit(content=f"⚠️ Scan failed: {e!r}")
            return
        stop.set();
        await spin_task

        if not matches:
            await msg.edit(content="✅ Done. No matches found.")
            return

        # summarize results without spamming follow-ups
        lines = [f"• {', '.join(m.get('terms', []))} — {m.get('url')}" for m in matches[:10]]
        more = f"\n…and {len(matches) - 10} more." if len(matches) > 10 else ""
        await msg.edit(content="✅ Done. Found:\n" + "\n".join(lines) + more)

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
