import os, re, json, hashlib, html
from datetime import datetime, timezone

try:
    from zoneinfo import ZoneInfo
except Exception:
    ZoneInfo = None

from urllib import request, parse

SIGNS = [
    ('aries', '白羊座', '♈'), ('taurus', '金牛座', '♉'), ('gemini', '双子座', '♊'),
    ('cancer', '巨蟹座', '♋'), ('leo', '狮子座', '♌'), ('virgo', '处女座', '♍'),
    ('libra', '天秤座', '♎'), ('scorpio', '天蝎座', '♏'), ('sagittarius', '射手座', '♐'),
    ('capricorn', '摩羯座', '♑'), ('aquarius', '水瓶座', '♒'), ('pisces', '双鱼座', '♓')
]

TIP_BUCKET = [
    '把注意力放在重要的人和事上', '试着早睡早起，效率更高', '大胆一点，会有惊喜发生', '别急于求成，稳扎稳打',
    '适合整理收纳与复盘思考', '多倾听，少争辩，事半功倍', '克制情绪，保持耐心', '尝试做一点运动，焕新状态',
    '今日适合学习和吸收新知', '给自己一个小目标并完成它', '与老朋友联络会带来好运', '少刷手机，专注当下',
    '主动表达想法，有人会响应', '避免冲动消费，理性一点', '把复杂问题拆解成小步', '做个小小的善举，运势+1',
    '清晰边界，拒绝无效内耗', '记录灵感，立刻行动一个', '保持好奇，发问与探索', '拥抱变化，相信直觉',
    '今天适合开始新计划', '复盘最近一周的收获', '把待办清单精简到三件', '尝试番茄工作法',
    '和家人好好吃顿饭', '整理邮件与消息收件箱', '鼓励身边的人，也鼓励自己', '学一点微小的新技能',
    '减少抱怨，多做一点', '给未来的自己写一封信', '喝足够的水，保持清醒', '站起来伸展 5 分钟',
    '不要拖延，从最难的开始', '完成一件长期回避的小事', '听一首让你振奋的歌', '阅读 10 页书',
    '给同事或朋友一句感谢', '优化一个重复流程', '减少无意义的对比', '接受不完美，继续前进',
    '用数据说话，用事实决策', '保持学习节奏，稳步积累', '把手机静音 30 分钟', '注意用眼健康',
    '今天早点结束工作', '设定边界，拒绝额外负担', '复习旧笔记，温故知新', '列出三件值得感恩的事',
    '保持专注，减少上下文切换', '对重要任务设置时间块', '提前准备明天的待办', '清理桌面，重启状态',
    '留出独处的时间', '把想法画成草图', '进行一次思维导图', '关注长期价值而非短期噪音',
    '写下今天最开心的瞬间', '回顾目标与进度', '和志同道合的人交流', '保持耐心，等待发芽',
    '今天适合做减法', '把流程标准化并记录', '分清紧急与重要', '专注过程，不执着结果',
    '给自己一点奖励', '把问题换个角度看', '从错误中提取经验', '尝试做一个小实验',
    '把知识输出成一段笔记', '优化一次重复性的任务', '提前十分钟出发', '主动请求反馈',
    '把复杂事拆成清晰清单', '试试晨间或晚间例会', '把能两分钟完成的事立刻做', '今天温柔地对自己',
    '减少糖分与熬夜', '适当午休，恢复精力', '不和过去较劲，向前看', '用清单可视化进展',
    '与其担心不如行动', '想一想“真正重要的是什么”', '把承诺写下来', '给自己一点安静',
    '拥抱随机性与小惊喜', '主动提出一个改进建议', '备份重要资料', '学会说“不”也说“好”',
    '关注健康，适量运动', '学习一个键盘快捷键', '打磨一个小作品', '把目标说给靠谱的人听',
    '用问题引导思考', '复盘一次沟通是否清晰', '表达清楚边界与预期', '尝试冥想三分钟',
    '今天适合整理账目', '理性看待得失', '启动而非等待完美', '选择最小可行步骤',
    '感谢当下，珍惜眼前人', '保持专业与善意', '把任务排优先级', '删掉一个无效订阅',
    '专注当下的一小步', '对自己宽容，对目标坚定', '用灵活替代僵化', '别怕求助，协作更强',
    '保持信息整洁，减少噪音', '今天对自己说“干得好”', '避免过度承诺', '用心倾听真实需求',
    '拆掉心理墙，迈出一步', '善待身体，早睡早起', '练习清晰表达', '让环境为你服务',
    '做个靠谱的人，按时交付', '给出具体且可执行的建议', '追踪一次微小的进步', '完成比完美更重要',
    '保持谦逊与锋芒', '慢就是稳，稳就是快', '一次只做一件事', '把目标写在显眼处',
    '减少内耗，保护专注力', '用复盘取代懊悔', '主动建立正向循环', '保持节奏，不急不徐'
]

def fallback_tip(sign_idx: int, day_of_year: int) -> str:
    # 线性轮换：确保连续 7 天不重复（TIP_BUCKET 长度 >= 7）
    idx = (day_of_year + sign_idx * 7) % len(TIP_BUCKET)
    return TIP_BUCKET[idx]

def fetch_tip(sign_en: str, sign_idx: int, day_of_year: int):
    url = f"https://aztro.sameerkumar.website/?sign={parse.quote(sign_en)}&day=today"
    try:
        req = request.Request(url, method='POST', data=b'')
        with request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        desc = (data.get('description') or '').strip()
        if not desc:
            raise ValueError('empty description')
        tip = desc.split('.') [0].split('。')[0].strip()
        tip = (tip[:80] + '…') if len(tip) > 80 else tip
        return tip
    except Exception:
        return fallback_tip(sign_idx, day_of_year)

def build_section():
    tz = os.getenv('HORO_TZ', '').strip() or 'Asia/Shanghai'
    tzname = tz
    try:
        z = ZoneInfo(tzname) if ZoneInfo else None
    except Exception:
        z = None
    now_dt = datetime.now(z if z else timezone.utc)
    date_str = now_dt.strftime('%Y-%m-%d')
    date_key = now_dt.strftime('%Y%m%d')

    lines = []
    title = f"🔮 Daily Horoscope Tips • {date_str} ({tzname})"
    lines.append(f"<p align=\"center\">")
    lines.append(f"<strong>{html.escape(title)}</strong><br/>")
    day_of_year = now_dt.timetuple().tm_yday
    for i, (en, zh, sym) in enumerate(SIGNS):
        tip = fetch_tip(en, i, day_of_year)
        item = f"{sym} {zh} {en.title()}: {tip}"
        lines.append(f"{html.escape(item)}<br/>")
    # 今日幸运星座（按天轮换，稳定且每天不同）
    lucky_idx = day_of_year % len(SIGNS)
    l_en, l_zh, l_sym = SIGNS[lucky_idx]
    lucky_line = f"✨ 今日幸运星座：{l_sym} {l_zh} {l_en.title()}"
    lines.append(f"<br/>{html.escape(lucky_line)}")
    lines.append("</p>")
    return "\n".join(lines) + "\n"

start = '<!-- DAILY-UPDATE:START -->'
end = '<!-- DAILY-UPDATE:END -->'
section = build_section()
new_block = f"{start}\n{section}{end}"

path = 'README.md'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

if start in content and end in content:
    pattern = re.compile(r"<!-- DAILY-UPDATE:START -->(.|\n)*?<!-- DAILY-UPDATE:END -->", re.M)
    updated = pattern.sub(new_block, content)
else:
    updated = content.rstrip() + "\n\n" + new_block + "\n"

if updated != content:
    with open(path, 'w', encoding='utf-8') as f:
        f.write(updated)
    print('README updated')
else:
    print('No change in README')
