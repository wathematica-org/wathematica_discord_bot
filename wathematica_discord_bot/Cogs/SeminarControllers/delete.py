import config
import discord
import utility_methods as ut
from database import async_session
from discord import Option
from discord.commands import slash_command
from discord.ext import commands
from model import Seminar
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound


class Delete(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @commands.guild_only()
    @slash_command(
        name="delete",
        description="[要編集権限] 名前が seminar_name のゼミを削除します。",
        guild_ids=config.guilds,
    )
    async def delete(
        self,
        ctx: discord.ApplicationContext,
        seminar_name: Option(input_type=str, description="削除対象のゼミ名", required=True),  # type: ignore
    ):

        # this command must be executed by the leader of the seminar
        # or by someone who has the manage_channels permission
        async with async_session() as session:
            async with session.begin():
                try:
                    this_seminar: Seminar = (
                        await session.execute(
                            select(Seminar).where(Seminar.name == seminar_name)
                        )
                    ).scalar_one()
                    current_leader_id = this_seminar.leader_id
                    role_setting_message_id = this_seminar.role_setting_message_id
                except NoResultFound:
                    embed = discord.Embed(
                        title="<:x:960095353577807883> データベース検索失敗",
                        description=f"`{seminar_name}` はデータベースに存在しません。管理者に連絡し手動で対応してもらってください。",
                        color=discord.Colour.red(),
                    )
                    await ctx.respond(embed=embed)
                    return

        if not (
            current_leader_id == ctx.author.id
            or ctx.author.guild_permissions.manage_channels
        ):
            embed = discord.Embed(
                title="<:x:960095353577807883> ゼミ終了処理失敗",
                description="現在のゼミ長のみがゼミを終了できます。",
                color=discord.Colour.red(),
            )
            await ctx.respond(embed=embed)
            return

        # ignore if this command is called in the exact channel that is to be deleted
        if ctx.channel.name == seminar_name:
            embed = discord.Embed(
                title="<:x:960095353577807883> ゼミ削除処理失敗",
                description="削除対象のチャンネル内からはコマンドを実行できません。",
                color=discord.Colour.red(),
            )
            await ctx.respond(embed=embed)
            return

        # keep in mind that ctx.channel and seminar_name are not the same
        # delete the text channel
        seminar_text_channel = await ut.get_text_channel_by_channel_name(
            scope=ctx.guild, channel_name=seminar_name
        )
        if seminar_text_channel:
            await seminar_text_channel.delete(reason=f"Requested by {ctx.author.name}")
            embed = discord.Embed(
                title="<:white_check_mark:960095096563466250> チャンネル削除成功",
                description=f"チャンネル `{seminar_name}` を削除しました。",
                color=discord.Colour.brand_green(),
            )
            await ctx.respond(embed=embed)
        else:
            embed = discord.Embed(
                title="<:x:960095353577807883> チャンネル削除失敗",
                description=f"`{seminar_name}` という名前のチャンネルは存在しません。",
                color=discord.Colour.red(),
            )
            await ctx.respond(embed=embed)

        # delete the role
        role = await ut.get_role_by_role_name(guild=ctx.guild, role_name=seminar_name)
        if role:
            await role.delete(reason=f"Requested by {ctx.author.name}")
            embed = discord.Embed(
                title="<:white_check_mark:960095096563466250> ロール削除成功",
                description=f"ロール `{seminar_name}` を削除しました。",
                color=discord.Colour.brand_green(),
            )
            await ctx.respond(embed=embed)
        else:
            embed = discord.Embed(
                title="<:x:960095353577807883> ロール削除失敗",
                description=f"`{seminar_name}` という名前のロールは存在しません。",
                color=discord.Colour.yellow(),
            )
            await ctx.respond(embed=embed)

        # delete the message in role_settings channel
        role_channel = await ut.get_text_channel_by_channel_name(
            scope=ctx.guild, channel_name=config.channel_names["role_settings"]
        )
        role_setting_message = await role_channel.fetch_message(
            id=role_setting_message_id
        )
        if role_setting_message:
            role_setting_message.delete()
            embed = discord.Embed(
                title="<:white_check_mark:960095096563466250> ロール付与メッセージ削除成功",
                description=f"{role_channel.mention} のロール付与メッセージを削除しました。",
                color=discord.Colour.brand_green(),
            )
            await ctx.respond(embed=embed)
        else:
            embed = discord.Embed(
                title="<:warning:960146803846684692> ロール付与メッセージ削除失敗",
                description=f"{role_channel.mention} にロール付与メッセージが存在しません。",
                color=discord.Colour.yellow(),
            )
            await ctx.respond(embed=embed)

        # delete this seminar from the database
        async with async_session() as session:
            async with session.begin():
                seminar_to_delete: Seminar = (
                    await session.execute(
                        select(Seminar).where(
                            Seminar.channel_id == seminar_text_channel.id
                        )
                    )
                ).scalar_one()
                await session.delete(seminar_to_delete)


def setup(bot: discord.Bot):
    bot.add_cog(Delete(bot))
