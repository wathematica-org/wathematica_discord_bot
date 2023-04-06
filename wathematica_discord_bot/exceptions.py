import discord


class InvalidCategoryException(discord.CheckFailure):
    pass


class InvalidChannelTypeException(discord.CheckFailure):
    pass
