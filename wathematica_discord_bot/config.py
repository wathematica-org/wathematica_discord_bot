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
    "ongoing_seminars": {
        "id": 822744303348482068,
        "name": "ゼミ(本運用)",
    },
    "pending_seminars": {
        "id": 821747045315641435,
        "name": "ゼミ(仮立て)",
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

# Discord server-specific settings
guilds: list[int] = [818049388986236938]
