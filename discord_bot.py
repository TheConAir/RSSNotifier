# discord_bot.py
import asyncio
from typing import Optional
import io
from collections import defaultdict
import time
import discord
from discord.ext import commands
from discord.commands import SlashCommandGroup, Option, AutocompleteContext

# ---- build the bot (no network I/O here) ----
def build_bot(searcher, guild_id: Optional[int] = None) -> commands.Bot:
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix="!", intents=intents)

    def _format_url_list(urls, limit=5):
        lines = [f"• {u}" for u in urls[:limit]]
        if len(urls) > limit:
            lines.append(f"...and {len(urls) - limit} more.")
        return "\n".join(lines)

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

    async def get_current_search_terms(ctx: discord.AutocompleteContext):
        q = (ctx.value or "").lower()
        terms = [str(t) for t in searcher.get_search_terms()]
        if q:
            terms = [t for t in terms if q in t.lower()]
        return terms[:25]

    @alerts.command(name="remove", description="Remove current search terms")
    async def remove_(ctx: discord.ApplicationContext, term: discord.Option(str, "Term to remove", autocomplete=discord.utils.basic_autocomplete(get_current_search_terms))):
        await ctx.defer(ephemeral=True)
        searcher.remove_search_term(term)
        await ctx.followup.send("Search term: \"" + term + "\" removed from the list.", ephemeral=True)

    @alerts.command(name="rescan", description="Rescan all items in RSS feed with current search terms")
    async def rescan_(ctx: discord.ApplicationContext):
        await ctx.defer(ephemeral=True)

        terms = searcher.get_search_terms()
        terms_text = ", ".join(terms) if terms else "—"

        # progress message + spinner
        progress = await ctx.followup.send(f"⏳ Scanning all items for: {terms_text}", ephemeral=True)
        stop = asyncio.Event()

        async def animate():
            frames = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
            i = 0
            while not stop.is_set():
                await progress.edit(content=f"{frames[i % len(frames)]} Scanning all items for: {terms_text}")
                i += 1
                await asyncio.sleep(0.2)

        spinner_task = asyncio.create_task(animate())

        # run the blocking scan off the event loop
        try:
            matches = await asyncio.to_thread(searcher.find_matches)
        finally:
            stop.set()
            await spinner_task  # wait for spinner to exit cleanly

        if not matches:
            await progress.edit(content="✅ Done. No matches found.")
            return

        # Group URLs by matched term
        by_term = defaultdict(list)
        all_lines = []
        for m in matches:
            url = m["url"]
            matched_terms = m["terms"] if isinstance(m["terms"], (list, tuple, set)) else [m["terms"]]
            for t in matched_terms:
                t = str(t)
                by_term[t].append(url)
                all_lines.append(f"{t}: {url}")

        total = sum(len(v) for v in by_term.values())

        embed = discord.Embed(
            title="Rescan complete",
            description=f"Found **{total}** matches across **{len(by_term)}** term(s).",
            color=0x2ecc71,
        )

        # attach TXT only if any term has > 5 URLs
        includeTXT = any(len(urls) > 5 for urls in by_term.values())

        # Show up to 5 terms (each with up to 5 URLs)
        for term, urls in list(by_term.items())[:5]:
            embed.add_field(
                name=f"{term} — {len(urls)}",
                value=_format_url_list(urls, limit=5),
                inline=False,
            )

        if includeTXT and len(by_term) > 5:
            embed.set_footer(text=f"+ {len(by_term) - 5} more term(s) in the attached file")

        await progress.edit(content="✅ Done. Found matches:")

        if includeTXT:
            text = "\n".join(all_lines) or "No results"
            buf = io.BytesIO(text.encode("utf-8"))
            file = discord.File(buf, filename="rescan_results.txt")
            await ctx.followup.send(embed=embed, file=file, ephemeral=True)
        else:
            await ctx.followup.send(embed=embed, ephemeral=True)

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
