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


class Rename(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @commands.guild_only()
    @slash_command(
        name="rename",
        description="ゼミを改名します。テキストチャンネルとロールの名前が変化します。",
        guild_ids=config.guilds,
    )
    async def rename(
        self,
        ctx: discord.ApplicationContext,
        new_name: Option(input_type=str, description="新しいゼミ名", required=True),  # type: ignore
    ):

        # ignore if the channel in which this command is called is not in either ongoing_seminars or pending_seminars
        if ctx.channel.category.name not in (
            config.category_names["ongoing_seminars"],
            config.category_names["pending_seminars"],
        ):
            embed = discord.Embed(
                title="<:x:960095353577807883> 不正な操作です",
                description=f'{config.category_names["ongoing_seminars"]}または{config.category_names["pending_seminars"]}にあるテキストチャンネルでのみ実行可能です。',
                color=discord.Colour.red(),
            )
            await ctx.respond(embed=embed)
            return

        # ensure that there's no existing seminar whose name is new_name
        if ut.get_text_channel_by_channel_name(scope=ctx.guild, channel_name=new_name):
            embed = discord.Embed(
                title="<:x:960095353577807883> ゼミ名変更失敗",
                description=f"`{new_name}` という名前のゼミは既に存在します。",
                color=discord.Colour.red(),
            )
            await ctx.respond(embed=embed)
            return

        current_name = ctx.channel.name
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
        role = await ut.get_role_by_role_name(guild=ctx.guild, role_name=current_name)
        if not role:
            embed = discord.Embed(
                title="<:x:960095353577807883> ロール名変更失敗",
                description=f"`{current_name}` という名前のロールは存在しません。",
                color=discord.Colour.red(),
            )
            await ctx.respond(embed=embed)
            return

        await role.edit(name=new_name.lower(), reason=f"Requested by {ctx.author.name}")
        embed = discord.Embed(
            title="<:white_check_mark:960095096563466250> ロール名変更成功",
            description=f"ロール名を `{new_name}` に更新しました。",
            color=discord.Colour.brand_green(),
        )
        await ctx.respond(embed=embed)

        async with async_session() as session:
            async with session.begin():
                try:
                    this_seminar: Seminar = (
                        await session.execute(
                            select(Seminar).where(Seminar.channel_id == ctx.channel.id)
                        )
                    ).scalar_one()
                    this_seminar.name = new_name.lower()
                except NoResultFound:
                    embed = discord.Embed(
                        title="<:warning:960146803846684692> データベース編集失敗",
                        description="このゼミはデータベースに存在しません。",
                        color=discord.Colour.yellow(),
                    )
                    await ctx.respond(embed=embed)

        # edit the message that is already sent to role_settings channel
        role_channel = await ut.get_text_channel_by_channel_name(
            scope=ctx.guild, channel_name=config.channel_names["role_settings"]
        )
        async for message in role_channel.history(limit=300):
            if message.author.name != config.bot_name:
                continue

            embed_objects_in_the_message: list[discord.Embed] = message.embeds
            if not embed_objects_in_the_message:
                # messages from old bot does not have embed object.
                continue

            # each message in role_settings channel has only one embed object
            embed_object_in_the_message = embed_objects_in_the_message[0]
            seminar_name_in_the_message = embed_object_in_the_message.title

            if seminar_name_in_the_message == current_name:
                new_embed = discord.Embed(
                    title=new_name,
                    description=f"{new_name} に参加する方はこのメッセージにリアクションをつけてください。",
                )
                await message.edit(embed=new_embed)
                break

        embed = discord.Embed(
            title="<:white_check_mark:960095096563466250> ロール付与メッセージ変更成功",
            description=f"{role_channel.mention} のロール付与メッセージを更新しました。",
            color=discord.Colour.brand_green(),
        )
        await ctx.respond(embed=embed)


def setup(bot: discord.Bot):
    bot.add_cog(Rename(bot))
