import discord


class InvalidCategoryException(discord.CheckFailure):
    pass


class InvalidChannelTypeException(discord.CheckFailure):
    pass


class ConfigurationNotCompleteException(discord.CheckFailure):
    pass


class SystemChannelOnlyException(discord.CheckFailure):
    pass
