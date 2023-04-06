import config
import discord
from discord import Option
from discord.commands import slash_command
from discord.ext import commands


class Schedule(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @commands.guild_only()
    @slash_command(
        name="schedule",
        description="日程調整用のメッセージを送信します。",
        guild_ids=config.guilds,
    )
    async def schedule(
        self,
        ctx: discord.ApplicationContext,
        only_weekdays: Option(input_type=bool, description="平日のみ表示", required=False),  # type: ignore
        only_late_hours: Option(input_type=bool, description="4限目以降のみ表示", required=False),  # type: ignore
    ):
        await ctx.defer()

        days_ = ["月", "火", "水", "木", "金", "土", "日"]
        reactions_ = [
            # Check Unicode emoji names here: https://emojipedia.org/
            "\N{Keycap Digit One}",
            "\N{Keycap Digit Two}",
            "\N{Keycap Digit Three}",
            "\N{Keycap Digit Four}",
            "\N{Keycap Digit Five}",
            "\N{Keycap Digit Six}",
        ]
        # TODO: Consider better implemenation
        days = days_[:5] if only_weekdays else days_
        reactions = reactions_[3:] if only_late_hours else reactions_

        for day in days:
            message = await ctx.send(day)
            for reaction in reactions:
                await message.add_reaction(reaction)
            await message.add_reaction("\N{Crying Face}")

        await ctx.respond("【日付調整】")


def setup(bot: discord.Bot):
    bot.add_cog(Schedule(bot))
