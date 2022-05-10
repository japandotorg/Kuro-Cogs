"""
MIT License

Copyright (c) 2021-present Kuro-Rui

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from asyncio import sleep
from random import choice, randint, shuffle
from string import ascii_letters, digits, punctuation

import discord
from redbot.core import commands
from redbot.core.utils.chat_formatting import humanize_list


def loading(step: int):
    l = ["▖", "▘", "▝", "▗"]
    screen = f"[{l[step]}]"
    return screen


class Hack(commands.Cog):
    """Le professional hecker."""

    def __init__(self, bot):
        self.bot = bot

    __author__ = humanize_list(["Kuro"])
    __version__ = "1.0.0"

    def format_help_for_context(self, ctx: commands.Context):
        """Thanks Sinbad!"""
        pre_processed = super().format_help_for_context(ctx)
        return (
            f"{pre_processed}\n\n"
            f"`Cog Author  :` {self.__author__}\n"
            f"`Cog Version :` {self.__version__}"
        )

    @commands.guild_only()
    @commands.cooldown(1, 25, commands.BucketType.channel)
    @commands.command(aliases=["heck"])
    async def hack(self, ctx, member: discord.Member):
        """Hack someone!"""

        if member == ctx.author:
            await ctx.send("Umm, please don't DOXX yourself \N{SKULL}")
            return

        # Mass editing lol
        message = await ctx.send(f"{loading(0)} Hacking {member.name} now...")
        await sleep(2)
        try:
            await message.edit(content=f"{loading(1)} Finding Discord Login...")
            await sleep(2)
            await message.edit(content=f"{loading(2)} Bypassing 2FA...")
            await sleep(3)
            domain = choice(
                [
                    "@aol.com",
                    "@disposablemail.com",
                    "@edu.com",
                    "@gmail.com",
                    "@gmx.net",
                    "@hotmail.com",
                    "@icloud.com",
                    "@msn.com"
                    "@outlook.com",
                    "@protonmail.com",
                    "@yahoo.com",
                    "@yandex.com"
                ]
            )
            email = member.name.replace(" ", "").replace("'", "").replace("\"", "") + domain
            letters = "".join(choice(ascii_letters) for letters in range(4))
            numbers = "".join(choice(digits) for numbers in range(3))
            puncts = "".join(choice(punctuation) for puncts in range(3))
            password = list(letters + numbers + puncts)
            shuffle(password)
            await message.edit(
                content=(
                    f"{loading(3)} Found login information:\n"
                    f"**Email**: `{email}`\n"
                    f"**Password**: `{password}`"
                )
            )
            await sleep(4)
            await message.edit(content=f"{loading(0)} Fetching user DMs...")
            await sleep(1)
            last_dm = choice(
                [
                    "I hope blueballs aren't real.",
                    "I hope noone sees my nudes folder.",
                    "I think it's smaller than most.",
                    "UwU",
                    "can I see your feet pics?",
                    "dont frgt to like and subscrube!!",
                    "honestly I'm pretty sure blue waffle is real and I have it.",
                    "imagine having a peen as small as mine in 2022",
                    "man I love my mommy.",
                    "pwetty pwease?",
                    "yeah I'm just built different.",
                    "yeah she goes to another school.",
                ]
            )
            await message.edit(content=f"{loading(1)} **Last DM**: `{last_dm}`")
            await sleep(3)
            await message.edit(content=f"{loading(2)} Injecting trojan virus into {member}...")
            await sleep(2)
            await message.edit(content=f"{loading(3)} Virus injected. Finding IP Address...")
            await sleep(3)
            # A valid IP address must be in the form of x.x.x.x, where x is a number from 0-255.
            ip_address = f"{randint(0, 255)}.{randint(0, 255)}.{randint(0, 255)}.{randint(0, 255)}"
            await message.edit(content=f"{loading(0)} **IP Address**: `{ip_address}`")
            await sleep(2)
            await message.edit(content=f"{loading(1)} Selling user data to the government...")
            await sleep(2)
            await message.edit(
                content=f"{loading(2)} Reporting account to Discord for breaking ToS..."
            )
            await sleep(1)
            await message.edit(content=f"{commands.context.TICK} Finished hacking {member.name}.")
            await ctx.send("The *totally* real and dangerous hack is complete.")
        except discord.NotFound:
            await ctx.send("Process terminated. The hack failed.")
            return
