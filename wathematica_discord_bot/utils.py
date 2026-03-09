import discord
from database import async_session
from sqlalchemy import select
from model import SeminarState, Category
from exceptions import CategoryNotRegisteredException, CategoryUnavailableException


async def get_category(
    ctx: discord.ApplicationContext, state: SeminarState, limit_count: bool = True
) -> discord.CategoryChannel:
    # find PENDING category
    async with async_session() as session:
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
        raise CategoryNotRegisteredException

    target_category: discord.CategoryChannel | None = None
    for cat_record in records:
        cat = ctx.guild.get_channel(cat_record.category_id)
        if not isinstance(cat, discord.CategoryChannel):
            continue

        if limit_count and len(cat.channels) < 45:
            target_category = cat
            break

    if not target_category:
        raise CategoryUnavailableException

    return target_category
