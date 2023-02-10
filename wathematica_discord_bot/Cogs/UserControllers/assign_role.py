import config
import discord
from database import async_session
from discord.ext import commands
from model import Seminar
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound


class RoleAssigner(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        member = payload.member
        if not member:
            return
        # ignore reactions from bot
        if member.bot:
            return
        # ignore reactions that happens in channels other than role_setting channel
        if payload.channel_id != config.channel_info["role_settings"]["id"]:
            return
        # react only to "interesting" emoji
        if payload.emoji.id != 836259755302453299:
            return
        # ignore reactions attached to messages other than bot's message
        channel = self.bot.get_channel(payload.channel_id)
        if not isinstance(channel, discord.TextChannel):
            return
        message = await channel.fetch_message(payload.message_id)
        if message.author.name != config.bot_name:
            return
        if not message.guild:
            return

        # check if the user who executed this command has permission to change the leader
        async with async_session() as session:
            async with session.begin():
                try:
                    this_seminar: Seminar = (
                        await session.execute(
                            select(Seminar).where(
                                Seminar.role_setting_message_id == payload.message_id
                            )
                        )
                    ).scalar_one()
                    seminar_name = this_seminar.name
                    role_id = this_seminar.role_id
                except NoResultFound:
                    embed = discord.Embed(
                        title="<:x:960095353577807883> データベース検索失敗",
                        description="このゼミはデータベースに存在しません。Carl-botでロールを取得するか、管理者に連絡してください。",
                        color=discord.Colour.red(),
                    )
                    await channel.send(
                        content=member.mention, embed=embed, delete_after=30
                    )
                    return

        seminar_role = message.guild.get_role(role_id)
        if not seminar_role:
            embed = discord.Embed(
                title="<:x:960095353577807883> ロール付与失敗",
                description=f"ロール `{seminar_name}` が存在しません。",
                color=discord.Colour.red(),
            )
            await message.channel.send(
                content=member.mention, embed=embed, delete_after=30
            )
        else:
            await member.add_roles(seminar_role)


def setup(bot: discord.Bot):
    bot.add_cog(RoleAssigner(bot))
