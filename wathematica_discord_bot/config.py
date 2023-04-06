from typing import TypedDict


# discord category is recognized as a special type of channel,
# so this object is named "ChannelInfo"
class ChannelInfo(TypedDict):
    id: int
    name: str


# Fundamental settings
bot_name: str = "Wathematica Bot"
category_info: dict[str, ChannelInfo] = {
    "general": {
        "id": 818049388986236941,
        "name": "全般",
    },
    "pending_seminars": {
        "id": 821747045315641435,
        "name": "ゼミ(仮立て)",
    },
    "ongoing_seminars": {
        "id": 822744303348482068,
        "name": "ゼミ(本運用)",
    },
    "paused_seminars": {
        "id": 935449084762935346,
        "name": "ゼミ(休止中)",
    },
    "finished_seminars": {
        "id": 853139587526164531,
        "name": "ゼミ(終了)",
    },
}
channel_info: dict[str, ChannelInfo] = {
    "role_settings": {
        "id": 828812752377610322,
        "name": "権限設定",
    },
}
# display error message for 30 seconds if the error is trivial
display_time_of_trivial_error: int = 30

# Discord server-specific settings
guilds: list[int] = [818049388986236938]
engineer_role_id: int = 822094687548342292
interesting_emoji_id: int = 836259755302453299
