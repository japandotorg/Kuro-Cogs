# Stolen some from https://github.com/kaogurai/cogs/blob/master/kaotools/kaotools.py (Ty alec)

import contextlib
import random
import re
import sys
import time
import urllib
from copy import copy

import aiohttp
import discord
import dislash
from dislash.interactions import ActionRow, Button, ButtonStyle

import redbot
from redbot.cogs.downloader.converters import InstalledCog
from redbot.core import Config, commands
from redbot.core.utils import AsyncIter
from redbot.core.utils.chat_formatting import box, humanize_list, pagify
from redbot.core.utils.menus import DEFAULT_CONTROLS, menu

from zalgo_text import zalgo

SUPPORT_SERVER = "https://discord.gg/Zef3pD8Yt5"


class KikiTools(commands.Cog):
    """
    Some tools for Kiki✨ that I hope useful.
    """

    __version__ = "1.1.0"

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=10023)
        default_global = {
            "blacklist": [],
            "whitelist": [],
        }
        self.config.register_global(**default_global)
        self.session = aiohttp.ClientSession()

    def cog_unload(self):
        del self.bot._connection.parsers["INTERACTION_CREATE"]
        self.bot.loop.create_task(self.session.close())

    def format_help_for_context(self, ctx):
        pre_processed = super().format_help_for_context(ctx)
        return f"{pre_processed}\n\nCog Version: {self.__version__}"

    @commands.Cog.listener()
    async def on_message_without_command(self, message: discord.Message):
        if message.author.bot:
            return
        if not message.guild:
            return
        if not message.channel.permissions_for(message.guild.me).send_messages:
            return
        if await self.bot.allowed_by_whitelist_blacklist(who=message.author) is False:
            return
        if not re.compile(rf"^<@!?{self.bot.user.id}>$").match(message.content):
            return
        prefixes = await self.bot.get_prefix(message.channel)
        if f"<@!{self.bot.user.id}> " in prefixes:
            prefixes.remove(f"<@!{self.bot.user.id}> ")
        sorted_prefixes = sorted(prefixes, key=len)
        if len(sorted_prefixes) > 500:
            return
        d = (
            f"Here are my prefixes in this server:\n{humanize_list(prefixes)}\n"
            f"You can type `{sorted_prefixes[0]}help` to view all commands!"
        )
        embed = discord.Embed(
            title="Hey There! <a:Kiki:922371688635707412>",
            colour=await self.bot.get_embed_colour(message.channel),
            description=d
        )
        await message.channel.send(embed=embed)

    @commands.command()
    @commands.bot_has_permissions(add_reactions=True, use_external_emojis=True)
    async def poll(self, ctx, *, question: str):
        """
        Create a simple poll.
        """
        if len(question) > 2000:
            await ctx.send("That question is too long.")
            return
        message = await ctx.send(f"**{ctx.author} asks:** " + question)
        await message.add_reaction("<:LalaOk:922835155712884777>")
        await message.add_reaction("<:KikiNo:922835155226345563>")

    @commands.command(aliases=["pickuser", "randommember", "picksomeone"])
    @commands.guild_only()
    async def randomuser(self, ctx):
        """
        Pick a random user in the server.
        """
        await ctx.send(f"<@{random.choice(ctx.guild.members).id}>")

    @commands.command(aliases=["av"])
    @commands.bot_has_permissions(embed_links=True)
    async def avatar(self, ctx, user: discord.User = None):
        """
        Get a user's avatar.
        """
        if not user:
            user = ctx.author
        png = user.avatar_url_as(format="png", size=4096)
        jpg = user.avatar_url_as(format="jpg", size=4096)
        gif = user.avatar_url_as(static_format="png", size=4096)
        size_512 = user.avatar_url_as(size=512)
        size_1024 = user.avatar_url_as(size=1024)
        size_2048 = user.avatar_url_as(size=2048)
        size_4096 = user.avatar_url_as(size=4096)
        m = (
            f"Formats: [PNG]({png}) | [JPG]({jpg}) | [GIF]({gif})\n"
            f"Sizes: [512]({size_512}) | [1024]({size_1024}) | [2048]({size_2048}) | [4096]({size_4096})"
        )
        embed = discord.Embed(
            color=await ctx.embed_color(),
            title=f"{user.name}'s Avatar:",
            description=m,
        )
        embed.set_image(url=user.avatar_url_as(size=4096))
        await ctx.send(embed=embed)

    @commands.command()
    async def vowelify(self, ctx: commands.Context, *, text: str):
        """
        Multiplies all vowels in a sentence.
        """
        uwuified = "".join(
            [
                c if c in "aeiouAEIOU" else (c * 3 if c not in "aeiou" else c)
                for c in text
            ]
        )
        await ctx.send(uwuified[:1000])

    @commands.command(aliases=["zalgoify"])
    async def zalgo(self, ctx: commands.Context, *, text: str):
        """
        Zalgoifies a sentence.
        """
        t = zalgo.zalgo().zalgofy(text)
        await ctx.send(t[:2000])

    @commands.bot_has_permissions(embed_links=True)
    @commands.command(aliases=["ship", "lovecalc"])
    async def lovecalculator(self, ctx, user: discord.User, user2: discord.User = None):
        """
        Calculates the amount of love between you and the bot.
        """
        love = random.randint(0, 100)
        if user2 is None:
            user2 = ctx.author
        ua = user.avatar_url_as(static_format="png")
        u2a = user2.avatar_url_as(static_format="png")
        u = f"https://api.martinebot.com/v1/imagesgen/ship?percent={love}&first_user={ua}&second_user={u2a}&no_69_percent_emoji=false"
        t = f"{user.name} and {user2.name} have {love}% compatibility."
        e = discord.Embed(color=await ctx.embed_color(), title=t)
        e.set_image(url=u)
        e.set_footer(text="Powered by api.martinebot.com")
        await ctx.send(embed=e)

    @commands.command(aliases=["peepee", "dingdong"])
    async def pp(self, ctx, *users: discord.Member):
        """
        Get user's peepee size!
        """
        if not users:
            users = (ctx.author,)

        penises = {}
        msg = ""
        state = random.getstate()

        for user in users:
            random.seed(user.id)

            dong_size = random.randint(0, 30)

            penises[user] = "8{}D".format("=" * dong_size)

        random.setstate(state)
        dongs = sorted(penises.items(), key=lambda x: x[1])

        for user, dong in dongs:
            msg += "**{}'s size:**\n{}\n".format(user.display_name, dong)

        for page in pagify(msg):
            await ctx.send(page)

    @commands.is_owner()
    @commands.command()
    async def updr(self, ctx, *cogs: InstalledCog):
        """Update cogs without questioning about reload."""
        ctx.assume_yes = True
        cog_update_command = ctx.bot.get_command("cog update")
        if not cog_update_command:
            await ctx.send(f"I can't find `{ctx.prefix}cog update` command")
            return
        await ctx.invoke(cog_update_command, *cogs)

    @commands.command()
    @commands.is_owner()
    async def unusedrepos(self, ctx):
        """View unused downloader repos."""
        repo_cog = self.bot.get_cog("Downloader")
        if not repo_cog:
            return await ctx.send("Downloader cog not found.")
        repos = [r.name for r in repo_cog._repo_manager.repos]
        active_repos = {c.repo_name for c in await repo_cog.installed_cogs()}
        for r in active_repos:
            try:
                repos.remove(r)
            except:
                pass
        if not repos:
            await ctx.send("All repos are currently being used!")
            return
        await ctx.send(f"Unused: \n" + box(repos, lang="py"))

    # The only thing I made by myself lol.
    @commands.command()
    @commands.bot_has_permissions(embed_links=True)
    async def vote(self, ctx):
        """Vote for me!"""
        c = await self.bot.get_embed_colour(await ctx.embed_color())
        t = "Please Vote for Me!"
        d = "You can vote for me by clicking on the links below:"
        f = "Thanks for your support!"
        i = ctx.bot.user.avatar_url
        
        dot = "<a:Dot:914352680627994634>"

        topgg_link = "https://top.gg/bot/886547720985264178/vote"
        dbl_link = "https://discordbotlist.com/bots/kiki/upvote"
        milrato_link = "https://milrato-botlist.eu/bot/886547720985264178/vote"
        # No links for https://discords.com because I haven't submitted the bot there yet.
        discords_link = ""

        e = discord.Embed(title = t, description=d, colour = c)
        e.add_field(name="Links:", value=f"{dot}[`Top.gg`]({topgg_link})\n{dot}[`Discord Bot List`]({dbl_link})\n{dot}[`Milrato Bot List`]({milrato_link})")
        e.set_thumbnail(url=i)
        e.set_footer(text=f)

        vote_button = [
            ActionRow(
                Button(
                    style=ButtonStyle.link,
                    label="Top.gg",
                    emoji=discord.PartialEmoji(name="topgg", animated=False, id="918280202398875758"),
                    url=topgg_link
                ),
                Button(
                    style=ButtonStyle.link,
                    label="discordbotlist.com",
                    emoji=discord.PartialEmoji(name="dbl", animated=False, id="757235965629825084"),
                    url=dbl_link
                ),
                Button(
                    style=ButtonStyle.link,
                    label="milrato-botlist.eu",
                    emoji=discord.PartialEmoji(name="OLD_Milrato", animated=False, id="840259659163893820"),
                    url=milrato_link
                )
            )
        ]
        await ctx.send(embed=e, components=vote_button)

    # Formatting stolen from Fixator10 :D
    @commands.command()
    @commands.bot_has_permissions(embed_links=True)
    async def credits(self, ctx):
        """Credits for everyone that makes this bot possible."""
        bot_name = "Kiki\✨"
        bot_name_without_backslash = "Kiki✨"
        owner = "K᲼u᲼r᲼o᲼#2740"
        since = "12ᵗʰ September 2021"

        t = f"{bot_name}'s Credits"
        d = f"Credits for all people and services that helps {bot_name} exist."
        c = await self.bot.get_embed_colour(await ctx.embed_color())
        i = "https://cdn.discordapp.com/attachments/908719687397953606/921065568365322280/kiki_round.png"
        f = f"{bot_name_without_backslash} exists since {since}."

        red = "<:Red:917079459641831474>"
        kiki = "<:Kiki:920617449127309322>"
        cog = "<:Cog:925401264395796481>"

        aikaterna = "[**aikaterna-cogs**](https://github.com/aikaterna/aikaterna-cogs): aikaterna (aikaterna#1393)"
        dualmoon = "[**Cogs.v3**](https://github.com/dualmoon/Cogs.v3): luna"
        cray = "[**cray-cogs**](https://github.com/i-am-zaidali/cray-cogs): crayyy_zee"
        dav = "[**Dav-Cogs**](https://github.com/Dav-Git/Dav-Cogs): Dav"
        fixator10 = "[**Fixator10-Cogs**](https://github.com/fixator10/Fixator10-Cogs): Fixator10"
        flame = "[**FlameCogs**](https://github.com/Flame442/FlameCogs): Flame442 (Flame#2941)"
        flapjack = "[**FlapJack-Cogs**](https://github.com/flapjax/FlapJack-Cogs): FlapJack"
        flare = "[**Flare-Cogs**](https://github.com/flaree/Flare-Cogs): flare (flare#0001)"
        zephyrkul = "[**FluffyCogs**](https://github.com/zephyrkul/FluffyCogs): Zephyrkul (Zephyrkul#1089)"
        bobloy = "[**Fox-V3**](https://github.com/bobloy/Fox-V3): Bobloy"
        jack = "[**JackCogs**](https://github.com/jack1142/JackCogs): jack1142 (Jackenmen#6607)"
        jintaku = "[**Jintaku-Cogs-V3**](https://github.com/Jintaku/Jintaku-Cogs-V3): Jintaku, Wyn"
        redjumpman = "[**Jumper-Plugins**](https://github.com/Redjumpman/Jumper-Plugins): Redjumpman (Redjumpman#1337)"
        kable = "[**Kable-Kogs**](https://github.com/kablekompany/Kable-Kogs): KableKompany (KableKompany#0001)"
        alec = "[**kaogurai/cogs**](https://github.com/kaogurai/cogs): alec"
        kennnyshiwa = "[**kennnyshiwa-cogs**](https://github.com/kennnyshiwa/kennnyshiwa-cogs): Kennnyshiwa, Beryju, Preda"
        kreusada = "[**Kreusada-Cogs**](https://github.com/kreusada/Kreusada-Cogs): Kreusada"
        laggron = "[**Laggrons-Dumb-Cogs**](https://github.com/retke/Laggrons-Dumb-Cogs): El Laggron"
        lastfm = "[**lastfm-red**](https://github.com/flaree/lastfm-red): flare(flare#0001), joinem (MisoBot), Fixator10, alec"
        max = "[**maxcogs**](https://github.com/ltzmax/maxcogs): MAX"
        npc = "[**npc-cogs**](https://github.com/npc203/npc-cogs): epic guy#0715"
        ob13 = "[**OB13-Cogs**](https://github.com/Obi-Wan3/OB13-Cogs): Obi-Wan3"
        ow0x = "[**owo-cogs**](https://github.com/ow0x/owo-cogs): ow0x (<@306810730055729152>)"
        palmtree5 = "[**palmtree5-cogs**](https://github.com/palmtree5/palmtree5-cogs): palmtree5"
        pcx = "[**PCXCogs**](https://github.com/PhasecoreX/PCXCogs): PhasecoreX (PhasecoreX#0635)"
        phen = "[**phen-cogs**](https://github.com/phenom4n4n/phen-cogs): PhenoM4n4n"
        preda = "[**predacogs**](https://github.com/PredaaA/predacogs): Predä"
        sauri = "[**SauriCogs**](https://github.com/elijabesu/SauriCogs): saurichable"
        kowlin = "[**Sentinel**](https://github.com/Kowlin/Sentinel): Kowlin#2536"
        sharky = "[**Sharky**](https://github.com/SharkyTheKing/Sharky): Sharky The King"
        tmerc = "[**tmerc-cogs**](https://github.com/tmercswims/tmerc-cogs): tmerc"
        tobo = "[**Tobo-Cogs**](https://github.com/Tobotimus/Tobo-Cogs): Tobotimus"
        neuro = "[**Toxic-Cogs**](https://github.com/NeuroAssassin/Toxic-Cogs): Neuro Assassin"
        trusty = "[**Trusty-cogs**](https://github.com/TrustyJAID/Trusty-cogs): TrustyJAID"
        vexed = "[**Vex-Cogs**](https://github.com/Vexed01/Vex-Cogs): Vexed (Vexed#9000)"
        wyn = "[**Wyn-RedV3Cogs**](https://github.com/TheWyn/Wyn-RedV3Cogs): Wyn"
        twentysix = "[**x26-Cogs**](https://github.com/Twentysix26/x26-Cogs): Twentysix (Twentysix#5252)"
        yami = "[**YamiCogs**](https://github.com/yamikaitou/YamiCogs): YamiKaitou#8975"

        c1 = f"{aikaterna}\n{dualmoon}\n{cray}\n{dav}\n{fixator10}\n{flame}\n{flapjack}\n{flare}\n{zephyrkul}\n{bobloy}\n{jack}\n{jintaku}"
        c2 = f"{redjumpman}\n{kable}\n{alec}\n{kennnyshiwa}\n{kreusada}\n{laggron}\n{lastfm}\n{max}\n{npc}\n{ob13}\n{ow0x}\n{palmtree5}\n{pcx}"
        c3 = f"{phen}\n{preda}\n{sauri}\n{kowlin}\n{sharky}\n{tmerc}\n{tobo}\n{neuro}\n{trusty}\n{vexed}\n{wyn}\n{twentysix}\n{yami}"

        e = discord.Embed(title = t, description=d, colour = c)
        e.add_field(
            name=f"{red} Red - Discord Bot",
            value=f"{bot_name} is an instance of [Red - Discord Bot](https://github.com/Cog-Creators/Red-DiscordBot), created by [Twentysix](https://github.com/Twentysix26) and improved by [many](https://github.com/Cog-Creators).\n[Red - Discord Bot](https://github.com/Cog-Creators/Red-DiscordBot) is maintained by an [awesome community].",
            inline=False
        )
        e.add_field(name=f"{kiki} Hosting", value=f"This instance is maintained by {owner}.", inline=False)
        e.add_field(name=f"{cog} Cogs & Their Creators", value=f"*Use `%findcog <command>` to find out who is author of certain command.*\n{c1}", inline=False)
        e.add_field(name="‎", value=f"{c2}", inline=False)
        e.add_field(name="‎", value=f"{c3}", inline=False)
        e.set_thumbnail(url=i)
        e.set_footer(text=f, icon_url=i)
        await ctx.send(embed=e)