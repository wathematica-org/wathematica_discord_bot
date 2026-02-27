import discord
from database import async_session
from sqlalchemy import select
from model import SeminarState, Category


state2name = {
    SeminarState.PENDING: "仮立て",
    SeminarState.ONGOING: "本運用",
    SeminarState.PAUSED: "休止中",
    SeminarState.FINISHED: "終了",
}


async def get_category(
    ctx: discord.ApplicationContext, state: SeminarState, limit_count: bool = True
) -> discord.CategoryChannel:
    # find PENDING category
    async with async_session() as session:
        # PENDING 用として登録されているカテゴリーをすべて取得
        records = (
            (
                await session.execute(
                    select(Category).where(
                        Category.guild_id == ctx.guild.id,
                        Category.state == state,
                    )
                )
            )
            .scalars()
            .all()
        )

    if not records:
        await ctx.respond(
            f":x: ゼミ({state2name[state]}) カテゴリーが登録されていません。管理者に `/setting` で設定を依頼してください。"
        )
        return

    target_category: discord.CategoryChannel | None = None
    for cat_record in records:
        cat = ctx.guild.get_channel(cat_record.category_id)
        if not isinstance(cat, discord.CategoryChannel):
            continue

        if limit_count and len(cat.channels) < 45:
            target_category = cat
            break

    if not target_category:
        await ctx.respond(
            f":warning: すべての ゼミ({state2name[state]}) カテゴリーが満杯です！新しくカテゴリーを作成して設定してください。"
        )
        return

    return target_category
