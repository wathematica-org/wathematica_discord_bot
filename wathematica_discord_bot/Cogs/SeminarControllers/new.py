import datetime

import config
import discord
import utility_methods as ut
from database import async_session
from discord import Option
from discord.commands import slash_command
from discord.ext import commands
from model import Seminar, SeminarState


class New(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @commands.guild_only()
    @slash_command(
        name="new",
        description="seminar_nameが付与されたテキストチャンネルとロールを作成します。",
        guild_ids=config.guilds,
    )
    async def new(
        self,
        ctx: discord.ApplicationContext,
        seminar_name: Option(input_type=str, description="新規ゼミ名", required=True),  # type: ignore
    ):
        # TODO: sanitize user's incorrect input patterns (e.g. some users may attach redundant quotation marks around the seminar name)
        seminar_name = seminar_name.lower()  # discord channel names should be lowercase

        # Check whether a text channel named {seminar_name} already exists
        if await ut.get_text_channel_by_channel_name(
            scope=ctx.guild, channel_name=seminar_name
        ):
            # When a text channel named {seminar_name} already exists
            seminar_name_suffix = 2
            while True:
                seminar_name_candidate = seminar_name + str(seminar_name_suffix)
                if await ut.get_text_channel_by_channel_name(
                    scope=ctx.guild, channel_name=seminar_name_candidate
                ):
                    seminar_name_suffix += 1
                else:
                    # found an available name
                    break
            embed = discord.Embed(
                title="<:warning:960146803846684692> チャンネル名の重複を検出しました",
                description=f"チャンネル `{seminar_name}` は既に存在します。新たに `{seminar_name_candidate}` を作成しますか？",
                color=discord.Colour.yellow(),
            )
            reply = await ctx.send(embed=embed)
            choices = ["\N{Squared OK}", "\N{Squared NG}"]
            for choice in choices:
                await reply.add_reaction(choice)
            # defer the final response. Without defer(), "The application did not respond" will show up to the user.
            await ctx.defer()
            # wait for a user's reaction
            try:
                # `lambda reaction,user: user == ctx.author` returns True if and only if the user who executed /new command
                # adds reaction to {reply}
                reaction, _ = await self.bot.wait_for(
                    "reaction_add",
                    timeout=30,
                    check=lambda _, user: user == ctx.author,
                )
            except TimeoutError:
                # delete the interaction message
                await reply.delete()
                embed = discord.Embed(
                    title="<:x:960095353577807883> タイムアウトしました",
                    description="制限時間内に応答がありませんでした。処理を中断します。",
                    color=discord.Colour.red(),
                )
                await ctx.respond(embed=embed)
                return
            else:
                # delete the interaction message
                await reply.delete()
                if reaction.emoji == "\N{Squared OK}":  # if the answer was :ok:
                    # update seminar name and proceed
                    seminar_name = seminar_name_candidate
                elif reaction.emoji == "\N{Squared NG}":  # if the answer was :ng:
                    embed = discord.Embed(
                        title="<:stop_button:1013296777027399700> 処理を中断します",
                        description="ゼミ作成の中断が要求されました。",
                        color=discord.Colour.blue(),
                    )
                    await ctx.respond(embed=embed)
                    return

        category = await ut.get_category_by_category_name(
            guild=ctx.guild,
            category_name=config.category_names["pending_seminars"],
        )
        new_text_channel = await category.create_text_channel(name=seminar_name)
        new_role = await ctx.guild.create_role(name=seminar_name, mentionable=True)

        embed = discord.Embed(
            title="<:white_check_mark:960095096563466250> チャンネル作成成功",
            description=f"チャンネル `{seminar_name}` を作成しました。",
            color=discord.Colour.brand_green(),
        )
        await ctx.respond(embed=embed)

        embed = discord.Embed(
            title="<:white_check_mark:960095096563466250> ロール作成成功",
            description=f"ロール `{seminar_name}` を作成しました。",
            color=discord.Colour.brand_green(),
        )
        await ctx.respond(embed=embed)

        # Send message to role_settings channel in order for users to attach the role to themselves
        role_setting_channel = await ut.get_text_channel_by_channel_name(
            scope=ctx.guild,
            channel_name=config.channel_names["role_settings"],
        )
        embed_to_role_settings_channel = discord.Embed(
            title=seminar_name,
            description=f"{seminar_name} に参加する方はこのメッセージにリアクションをつけてください。",
        )
        message_to_role_settings_channel: discord.Message = (
            await role_setting_channel.send(embed=embed_to_role_settings_channel)
        )
        await message_to_role_settings_channel.add_reaction(
            "<:interesting:836259755302453299>"
        )

        embed = discord.Embed(
            title="<:white_check_mark:960095096563466250> ゼミ作成成功",
            description=f"`{ctx.author.mention}` をゼミ長として登録しました。",
            color=discord.Colour.brand_green(),
        )
        await new_text_channel.send(embed=embed)

        # Prompt users to get the role at role_settings channel
        embed = discord.Embed(
            title="<:white_check_mark:960095096563466250> ロール付与メッセージ送信成功",
            description=f"このゼミに参加する方は {role_setting_channel.mention} でロールの取得を行ってください。",
            color=discord.Colour.brand_green(),
        )
        await new_text_channel.send(embed=embed)

        # add this seminar to the database
        seminar = Seminar(
            name=seminar_name,
            created_at=datetime.datetime.now(),
            finished_at=None,
            seminar_state=SeminarState.PENDING,
            leader_id=ctx.author.id,
            channel_id=new_text_channel.id,
            role_id=new_role.id,
            role_setting_message_id=message_to_role_settings_channel.id,
        )
        async with async_session() as session:
            async with session.begin():
                session.add(seminar)


def setup(bot: discord.Bot):
    bot.add_cog(New(bot))
