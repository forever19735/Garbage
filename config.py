"""
設定檔
儲存錯誤訊息範本和其他設定
"""

# 指令別名映射表（中文 -> 英文）
COMMAND_ALIASES = {
    '@設定時間': '@time',
    '@設定星期': '@day',
    '@設定排程': '@cron',
    '@設定成員': '@week',
    '@設定文案': '@message',
    '@查看排程': '@schedule',
    '@查看成員': '@members',
    '@查看狀態': '@status',
    '@幫助': '@help',
    '@說明': '@help',
    '@快速設定': '@quickstart',
    '@重置': '@reset_all',
}

# 所有可用指令列表（用於模糊匹配）
AVAILABLE_COMMANDS = [
    '@schedule', '@members', '@time', '@day', '@cron', '@week',
    '@addmember', '@removemember', '@message', '@help', '@status',
    '@firebase', '@backup', '@reset_date', '@clear_week', '@clear_members',
    '@clear_groups', '@reset_all', '@debug_env', '@quickstart'
]

# 錯誤訊息範本
ERROR_TEMPLATES = {
    'time_format': "❌ 時間格式錯誤\n📍 您輸入的：{input}\n⚠️ 問題：{issue}\n✅ 正確格式：@time 18:30\n💡 範例：@time 09:00 或 @time 17:30",
    'hour_range': "❌ 小時超出範圍\n📍 您輸入的小時：{hour}\n⚠️ 小時必須在 0-23 之間\n✅ 正確範例：@time 18:30",
    'minute_range': "❌ 分鐘超出範圍\n📍 您輸入的分鐘：{minute}\n⚠️ 分鐘必須在 0-59 之間\n✅ 正確範例：@time 18:30",
    'day_format': "❌ 星期格式錯誤\n📍 您輸入的：{input}\n⚠️ 支援的星期：mon, tue, wed, thu, fri, sat, sun\n✅ 正確範例：@day mon,thu 或 @day mon,wed,fri",
    'week_format': "❌ 週數格式錯誤\n📍 您輸入的：{input}\n⚠️ 週數必須是正整數（1, 2, 3...）\n✅ 正確範例：@week 1 Alice,Bob",
    'cron_format': "❌ 排程格式錯誤\n📍 您輸入的：{input}\n⚠️ 正確格式：@cron 星期 時:分\n✅ 正確範例：@cron mon,thu 18:30",
    'unknown_command': "❓ 找不到指令「{command}」\n\n{suggestions}\n💡 輸入 @help 查看所有指令",
}

# 指令描述
COMMAND_DESCRIPTIONS = {
    '@schedule': '查看推播排程',
    '@members': '查看成員輪值表',
    '@time': '設定推播時間',
    '@day': '設定推播星期',
    '@cron': '設定排程（星期+時間）',
    '@week': '設定週成員',
    '@addmember': '添加成員',
    '@removemember': '移除成員',
    '@message': '設定自訂文案',
    '@help': '查看幫助',
    '@status': '查看系統狀態',
    '@firebase': 'Firebase 狀態',
    '@backup': '建立備份',
    '@reset_date': '重置基準日期',
    '@clear_week': '清空指定週',
    '@clear_members': '清空所有成員',
    '@clear_groups': '清空群組',
    '@reset_all': '重置所有資料',
    '@debug_env': '環境變數診斷',
    '@quickstart': '快速設定',
}


def get_command_description(command: str) -> str:
    """取得指令的簡短描述"""
    return COMMAND_DESCRIPTIONS.get(command, '未知指令')
