# Fundamental settings
bot_name: str = "Wathematica Bot"
category_names: dict[str, str] = {
    "general": "全般",
    "ongoing_seminars": "ゼミ(本運用)",
    "pending_seminars": "ゼミ(仮立て)",
    "finished_seminars": "ゼミ(終了)",
}
channel_names: dict[str, str] = {"role_settings": "権限設定"}

# Discord server-specific settings
guilds: list[str] = ["818049388986236938"]
