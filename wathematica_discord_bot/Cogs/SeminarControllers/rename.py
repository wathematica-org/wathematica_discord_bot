import config
import discord
from checks import specific_categories_only, textchannel_only
from database import async_session
from discord import NotFound, Option
from discord.commands import slash_command
from discord.ext import commands
from exceptions import InvalidCategoryException, InvalidChannelTypeException
from model import Seminar, SeminarState
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound


class Rename(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @commands.guild_only()
    @specific_categories_only(
        category_ids=[
            config.category_info["pending_seminars"]["id"],
            config.category_info["ongoing_seminars"]["id"],
        ]
    )
    @textchannel_only()
    @slash_command(
        name="rename",
        description="ゼミを改名します。テキストチャンネルとロールの名前が変化します。",
        guild_ids=[config.guild_id],
    )
    async def rename(
        self,
        ctx: discord.ApplicationContext,
        new_name: Option(input_type=str, description="新しいゼミ名", required=True),  # type: ignore
    ):
        # [ give additional information to type checker
        assert isinstance(new_name, str)
        # guild_only() decorator ensures that ctx.guild is not None
        assert isinstance(ctx.guild, discord.Guild)
        # ]

        new_name = new_name.lower()  # discord channel names should be lowercase

        # ensure that `new_name` does not contain illegal characters
        if any(bad_symbol in new_name for bad_symbol in (" ", "\t", ".", ",")):
            embed = discord.Embed(
                title="<:x:960095353577807883> ゼミ名が不正です",
                description="ゼミ名に空白文字・カンマ・ピリオドを含めることはできません。",
                color=discord.Colour.red(),
            )
            await ctx.respond(embed=embed)
            return

        # ensure that there's no existing seminar whose name is new_name
        async with async_session() as session:
            async with session.begin():
                try:
                    (
                        await session.execute(
                            select(Seminar).where(
                                Seminar.name == new_name,
                                Seminar.seminar_state != SeminarState.FINISHED,
                                Seminar.server_id == ctx.guild_id,
                            )
                        )
                    ).scalar_one()
                except NoResultFound:
                    pass  # there's no problem because no duplicate was found
                else:
                    embed = discord.Embed(
                        title="<:x:960095353577807883> ゼミ名変更失敗",
                        description=f"`{new_name}` という名前のゼミは既に存在します。",
                        color=discord.Colour.red(),
                    )
                    await ctx.respond(embed=embed)
                    return

        async with async_session() as session:
            async with session.begin():
                try:
                    this_seminar: Seminar = (
                        await session.execute(
                            select(Seminar).where(
                                Seminar.channel_id == ctx.channel.id,
                                Seminar.server_id == ctx.guild_id,
                            )
                        )
                    ).scalar_one()
                    role_id = this_seminar.role_id
                    role_setting_message_id = this_seminar.role_setting_message_id
                    current_name = this_seminar.name
                except NoResultFound:
                    embed = discord.Embed(
                        title="<:x:960095353577807883> ゼミ名変更失敗",
                        description="このゼミはデータベースに存在しません。",
                        color=discord.Colour.yellow(),
                    )
                    await ctx.respond(embed=embed)
                    return
                else:
                    # change the name of text channel
                    await ctx.channel.edit(
                        name=new_name.lower(), reason=f"Requested by {ctx.author.name}"
                    )
                    embed = discord.Embed(
                        title="<:white_check_mark:960095096563466250> チャンネル名変更成功",
                        description=f"チャンネル名を `{new_name}` に更新しました。",
                        color=discord.Colour.brand_green(),
                    )
                    await ctx.respond(embed=embed)

                    # change the name of role
                    role = ctx.guild.get_role(role_id)
                    if role:
                        await role.edit(
                            name=new_name.lower(),
                            reason=f"Requested by {ctx.author.name}",
                        )
                        embed = discord.Embed(
                            title="<:white_check_mark:960095096563466250> ロール名変更成功",
                            description=f"ロール名を `{new_name}` に更新しました。",
                            color=discord.Colour.brand_green(),
                        )
                        await ctx.respond(embed=embed)
                    else:
                        embed = discord.Embed(
                            title="<:x:960095353577807883> ロール名変更失敗",
                            description=f"`{current_name}` という名前のロールは存在しません。",
                            color=discord.Colour.red(),
                        )
                        await ctx.respond(embed=embed)
                        return

                    # update the name of seminar in the database
                    this_seminar.name = new_name

        # edit the message that is already sent to role_settings channel
        role_channel = ctx.guild.get_channel(config.channel_info["role_settings"]["id"])
        if not isinstance(role_channel, discord.TextChannel):
            embed = discord.Embed(
                title="<:x:960095353577807883> システムエラー",
                description="管理者向けメッセージ: `role_settings` チャンネルが見つかりませんでした。",
                color=discord.Colour.red(),
            )
            await ctx.respond(embed=embed)
            return

        try:
            role_setting_message = await role_channel.fetch_message(
                role_setting_message_id
            )
        except NotFound:
            embed = discord.Embed(
                title="<:warning:960146803846684692> ロール付与メッセージ編集失敗",
                description=f"{current_name} のロール付与メッセージが見つかりませんでした。",
                color=discord.Colour.yellow(),
            )
            await ctx.respond(embed=embed)
        else:
            new_embed = discord.Embed(
                title=new_name,
                description=f"{new_name} に参加する方はこのメッセージにリアクションをつけてください。",
            )
            await role_setting_message.edit(embed=new_embed)
            embed = discord.Embed(
                title="<:white_check_mark:960095096563466250> ロール付与メッセージ編集成功",
                description=f"{role_channel.mention} のロール付与メッセージを編集しました。",
                color=discord.Colour.brand_green(),
            )
            await ctx.respond(embed=embed)

    @rename.error
    async def rename_error(
        self, ctx: discord.ApplicationContext, error: commands.CheckFailure
    ):
        if isinstance(error, InvalidChannelTypeException):
            embed = discord.Embed(
                title="<:x:960095353577807883> 不正な操作です",
                description="このコマンドはスレッド内では実行できません。",
                color=discord.Colour.red(),
            )
            await ctx.respond(embed=embed)
            return
        if isinstance(error, InvalidCategoryException):
            embed = discord.Embed(
                title="<:x:960095353577807883> 不正な操作です",
                description=f'{config.category_info["pending_seminars"]["name"]}または{config.category_info["ongoing_seminars"]["name"]}にあるテキストチャンネルでのみ実行可能です。',
                color=discord.Colour.red(),
            )
            await ctx.respond(embed=embed)
            return

        raise Exception("Unexpected error occurred.")


def setup(bot: discord.Bot):
    bot.add_cog(Rename(bot))
