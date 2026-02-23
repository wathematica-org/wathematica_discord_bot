import discord
from discord.ext import commands
from sqlalchemy import select

from database import async_session
from model import Guild, Category, SeminarState

from view.settings_view import get_settings_embed


class AutoSetup(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            await self._run_auto_setup(guild)

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        await self._run_auto_setup(guild)

    async def _run_auto_setup(self, guild: discord.Guild):
        system_channel_id = None  # 通知を送るためのチャンネルIDを覚えておく変数

        async with async_session() as session:
            async with session.begin():
                stmt = select(Guild).where(Guild.guild_id == guild.id)
                existing_guild = (await session.execute(stmt)).scalar_one_or_none()

                if existing_guild:
                    return

                print(f"[{guild.name}] Auto-configuring...")
                new_guild = Guild(guild_id=guild.id, name=guild.name)

                # --- チャンネルの検出 ---
                role_channels = [c for c in guild.text_channels if "権限設定" in c.name]
                if len(role_channels) == 1:
                    new_guild.role_setting_channel_id = role_channels[0].id

                system_channels = [
                    c for c in guild.text_channels if "system" in c.name.lower()
                ]
                if len(system_channels) == 1:
                    new_guild.system_channel_id = system_channels[0].id
                    # ▼ ここで system チャンネルの ID を記憶しておく
                    system_channel_id = system_channels[0].id

                # --- ロールの検出 ---
                engineer_roles = [r for r in guild.roles if "技術部" in r.name]
                if len(engineer_roles) == 1:
                    new_guild.engineer_role_id = engineer_roles[0].id

                # --- 絵文字の検出 ---
                interesting_emojis = [
                    e for e in guild.emojis if e.name == "interesting"
                ]
                if len(interesting_emojis) == 1:
                    new_guild.interesting_emoji_id = interesting_emojis[0].id

                session.add(new_guild)

                # --- カテゴリーの検出と登録 ---
                for cat in guild.categories:
                    state = None
                    if "ゼミ" in cat.name and "仮立て" in cat.name:
                        state = SeminarState.PENDING
                    elif "ゼミ" in cat.name and "本運用" in cat.name:
                        state = SeminarState.ONGOING
                    elif "ゼミ" in cat.name and "休止中" in cat.name:
                        state = SeminarState.PAUSED
                    elif "ゼミ" in cat.name and "終了" in cat.name:
                        state = SeminarState.FINISHED

                    if state:
                        new_cat = Category(
                            category_id=cat.id,
                            name=cat.name,
                            guild_id=guild.id,
                            state=state,
                            category_type="regular",
                        )
                        session.add(new_cat)

        # ---------------------------------------------------------
        # DBへの保存（コミット）が完全に終わった後の処理
        # ---------------------------------------------------------
        if system_channel_id:
            system_channel = guild.get_channel(system_channel_id)
            if isinstance(system_channel, discord.TextChannel):
                # DBから最新の状態を読み込んで、あのダッシュボードと同じEmbedを作成！
                embed = await get_settings_embed(guild.id, guild.name, self.bot)

                # 通知用にタイトルや説明文だけ少しアレンジする（上書き）
                embed.title = "✨ Botの初期セットアップが完了しました"
                embed.description = "サーバーの構成を自動検出し、以下の通り設定しました。\n手動で変更が必要な場合は `/setting` コマンドを使用してください。"
                embed.color = discord.Colour.brand_green()

                await system_channel.send(embed=embed)


def setup(bot: discord.Bot):
    bot.add_cog(AutoSetup(bot))
