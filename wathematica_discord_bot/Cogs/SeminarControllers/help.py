import textwrap

import config
import discord
from discord import Option
from discord.commands import slash_command
from discord.ext import commands


class Help(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    def generate_embed(self, command_name: str) -> discord.Embed:
        embed = discord.Embed(
            title="コマンドの使い方",
            color=0x12A0F0,  # blue
            description="<:bulb:1073594829528903681> 引数を取るコマンドを実行する際は, `/コマンド名` を入力して一度Enterを押すとスムーズに入力できることがあります。",
        )
        if command_name in ["all", "help"]:
            embed.add_field(
                name="/help [コマンド名]",
                value=textwrap.dedent(
                    """
                    `[コマンド名]` という名前のコマンドの使い方を表示します。
                    `[コマンド名]` を省略した場合は、全てのコマンドの使い方を表示します。
                    **`/help` コマンドの出力は、コマンドを実行した本人にのみ表示されます。**
                    """
                ),
                inline=False,
            )
        if command_name in ["all", "new"]:
            embed.add_field(
                name="/new <新規ゼミ名>",
                value=textwrap.dedent(
                    """
                    `<新規ゼミ名>` という名前の新しいゼミを作成します。
                    当該ゼミ用のテキストチャンネルとロールが生成されます。このコマンドの実行者はゼミ長となります。
                    """
                ),
                inline=False,
            )
        if command_name in ["all", "schedule"]:
            embed.add_field(
                name="/schedule [平日のみ表示する] [4限以降のみ表示する]",
                value=textwrap.dedent(
                    """
                    日程調整用のメッセージを送信します。
                    平日のみ表示したい場合は、/scheduleを入力すると出てくる `only_weekdays` オプションにTrueを指定してください。
                    4限以降のみ表示したい場合は、 `only_late_hours` オプションにTrueを指定してください。
                    特に指定が必要ない場合は、各オプションを省略することが出来ます。
                    """
                ),
                inline=False,
            )
        if command_name in ["all", "move"]:
            embed.add_field(
                name="/move",
                value=textwrap.dedent(
                    f"""
                    このゼミを本始動させます。
                    テキストチャンネルが{config.category_info["pending_seminars"]['name']}カテゴリから{config.category_info["ongoing_seminars"]['name']}カテゴリに移動します。
                    """
                ),
                inline=False,
            )
        if command_name in ["all", "rename"]:
            embed.add_field(
                name="/rename <更新後のゼミ名>",
                value=textwrap.dedent(
                    """
                    ゼミの名称を変更します。
                    テキストチャンネルとロールの名前が更新され、ロール付与メッセージも更新されます。
                    """
                ),
                inline=False,
            )
        if command_name in ["all", "end"]:
            embed.add_field(
                name="/end",
                value=textwrap.dedent(
                    f"""
                    このゼミを終了します。
                    テキストチャンネルが{config.category_info["finished_seminars"]['name']}に移動され、ロールとロール付与メッセージが削除されます。
                    **このコマンドはゼミ長のみが実行できます。**
                    """
                ),
                inline=False,
            )
        if command_name in ["all", "delete"]:
            embed.add_field(
                name="/delete <削除するゼミ名>",
                value=textwrap.dedent(
                    """
                    `<削除するゼミ名>` という名前のゼミを削除します。
                    テキストチャンネル、ロールとロール付与メッセージが削除されます。
                    **このコマンドはゼミ長のみが実行できます。**
                    """
                ),
                inline=False,
            )
        if command_name in ["all", "leader"]:
            embed.add_field(
                name="/leader",
                value=textwrap.dedent(
                    """
                    このゼミのゼミ長を表示します。
                    """
                ),
                inline=False,
            )
        if command_name in ["all", "chleader"]:
            embed.add_field(
                name="/chleader <ゼミ長にするユーザの指定名>",
                value=textwrap.dedent(
                    """
                    このゼミのゼミ長を変更します。ユーザは `Discordのユーザ名#4桁の識別子` の形で指定します。
                    詳細については、 `/chleader <適当な文字列>` を実行して確認してください。
                    **このコマンドはゼミ長のみが実行できます。**
                    """
                ),
                inline=False,
            )
        return embed

    @commands.guild_only()
    @slash_command(
        name="help",
        description="ヘルプを表示します。",
        guild_ids=config.guilds,
    )
    async def help(
        self,
        ctx: discord.ApplicationContext,
        command_name: Option(input_type=str, description="[省略可]解説を見たいコマンド名", required=False),  # type: ignore
    ):
        # [ give additional information to type checker
        # guild_only() decorator ensures that ctx.guild is not None
        assert isinstance(ctx.guild, discord.Guild)
        # ]

        # if command_name is not specified, show help for all commands
        if not command_name:
            command_name = "all"
        elif not self.bot.get_command(name=command_name, guild_ids=[ctx.guild.id]):
            embed = discord.Embed(
                title="<:x:960095353577807883> コマンドが存在しません。",
                description=f"`{command_name}` というコマンドは存在しません。",
                color=discord.Colour.red(),
            )
            await ctx.respond(embed=embed, ephemeral=True)
            return

        embed = self.generate_embed(command_name=command_name)
        await ctx.respond(embed=embed, ephemeral=True)


def setup(bot: discord.Bot):
    bot.add_cog(Help(bot))
