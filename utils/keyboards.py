"""
Saare inline keyboards — screenshot wale font + icon style me.
"""
from pyrogram.types import InlineKeyboardButton as IKB
from pyrogram.types import InlineKeyboardMarkup as IKM

import database as db
from utils.fonts import tc


def _b(icon, label, data):
    return IKB(f"{icon} {tc(label)}", callback_data=data)


# ───────────────────────────── ADMIN PANEL ─────────────────────────────
def admin_panel(user_id=0):
    ad = "ᴏɴ" if db.get_bool("auto_delete_on", True) else "ᴏғғ"
    pr = "ᴏɴ" if db.get_bool("protect") else "ᴏғғ"
    mt = "ᴏɴ" if db.get_bool("maintenance") else "ᴏғғ"
    fs = "ᴏɴ" if db.get_bool("force_sub") else "ᴏғғ"

    rows = [
        [_b("▪️", "Stats", "ap:stats"), _b("◉", "Users", "ap:users")],
        [_b("◆", "All Files", "ap:files"), _b("◆", "Batches", "ap:batches")],
        [_b("⚑", "Broadcast", "ap:bc"), _b("✘", "Ban / Unban", "ap:ban")],
        [_b("⊕", "Add Admin", "ap:addadmin"), _b("◇", "Admins", "ap:admins")],
        [_b("❖", "Auto Delete", "ap:autodel"), _b("✿", "Protect", "ap:protect")],
        [_b("⚙️", "Force Sub", "ap:fsub"), _b("◉", "Audit Log", "ap:logs")],
        [_b("⚙️", "Backup Db", "ap:backup"), _b("▣", "Security", "ap:sec")],
        [_b("⚠️", "Maintenance", "ap:maint"), _b("⚙️", "Settings", "ap:settings")],
        [IKB(f"✓ {tc('Auto Del')}: {ad}", callback_data="tg:auto_delete_on"),
         IKB(f"✿ {tc('Protect')}: {pr}", callback_data="tg:protect")],
        [IKB(f"⚑ {tc('F-Sub')}: {fs}", callback_data="tg:force_sub"),
         IKB(f"⚠️ {tc('Maint')}: {mt}", callback_data="tg:maintenance")],
        [_b("▲", "Start Photo", "ap:photo"), _b("↻", "Restart", "ap:restart")],
        [_b("✦", "System", "ap:system"), _b("✕", "Close", "ap:close")],
    ]
    return IKM(rows)


def back(to="ap:home", extra=None):
    rows = []
    if extra:
        rows.extend(extra)
    rows.append([IKB(f"« {tc('Back')}", callback_data=to),
                 IKB(f"✕ {tc('Close')}", callback_data="ap:close")])
    return IKM(rows)


# ───────────────────────────── SUB MENUS ─────────────────────────────
def stats_kb():
    return back(extra=[[IKB(f"↻ {tc('Refresh')}", callback_data="ap:stats"),
                        IKB(f"✦ {tc('System')}", callback_data="ap:system")]])


def users_kb():
    return back(extra=[[IKB(f"◉ {tc('Recent')}", callback_data="ap:users"),
                        IKB(f"✘ {tc('Banned')}", callback_data="ap:banned")],
                       [IKB(f"⚑ {tc('Export Ids')}", callback_data="ap:export")]])


def files_kb():
    return back(extra=[[IKB(f"◆ {tc('Recent')}", callback_data="ap:files"),
                        IKB(f"★ {tc('Top Opened')}", callback_data="ap:topfiles")]])


def autodel_kb():
    cur = db.get_int("auto_delete", 1800)
    opts = [("10 ᴍɪɴ", 600), ("30 ᴍɪɴ", 1800), ("1 ʜᴏᴜʀ", 3600),
            ("6 ʜᴏᴜʀs", 21600), ("24 ʜᴏᴜʀs", 86400), ("ᴏғғ", 0)]
    rows, line = [], []
    for label, val in opts:
        mark = "✅ " if val == cur else ""
        line.append(IKB(f"{mark}{label}", callback_data=f"set:auto_delete:{val}"))
        if len(line) == 3:
            rows.append(line)
            line = []
    if line:
        rows.append(line)
    return back(extra=rows)


def confirm_kb(action, arg=""):
    return IKM([[IKB(f"✓ {tc('Yes')}", callback_data=f"ok:{action}:{arg}"),
                 IKB(f"✘ {tc('No')}", callback_data="ap:home")]])


def bc_kb():
    return back(extra=[[IKB(f"⚑ {tc('All Users')}", callback_data="bc:all"),
                        IKB(f"✘ {tc('Cancel')}", callback_data="ap:home")]])


def fsub_kb():
    rows = []
    for ch in db.fsub_list():
        rows.append([IKB(f"✘ {tc('Remove')}: {ch['title'][:18]}",
                         callback_data=f"fsub:rm:{ch['chat_id']}")])
    return back(extra=rows)


def admins_kb():
    rows = []
    for uid in db.admin_ids():
        import config
        if uid == config.OWNER_ID:
            rows.append([IKB(f"★ {uid} ({tc('Owner')})", callback_data="noop")])
        else:
            rows.append([IKB(f"✘ {tc('Remove')} {uid}", callback_data=f"adm:rm:{uid}")])
    return back(extra=rows)


# ───────────────────────────── BATCH FLOW ─────────────────────────────
def batch_collect_kb(count=0):
    return IKM([
        [IKB(f"✓ {tc('Done')} ({count})", callback_data="batch:done")],
        [IKB(f"↺ {tc('Clear')}", callback_data="batch:clear"),
         IKB(f"✘ {tc('Cancel')}", callback_data="batch:cancel")],
    ])


def link_kb(link, code):
    return IKM([
        [IKB(f"▸ {tc('Open Link')}", url=link)],
        [IKB(f"⚑ {tc('Share')}", url=f"https://t.me/share/url?url={link}")],
        [IKB(f"✘ {tc('Revoke')}", callback_data=f"lnk:rv:{code}"),
         IKB(f"◉ {tc('Info')}", callback_data=f"lnk:in:{code}")],
    ])


# ───────────────────────────── USER SIDE ─────────────────────────────
def start_kb(is_adm=False):
    import config
    rows = [[IKB(f"◈ {tc('How To Use')}", callback_data="u:help"),
             IKB(f"◉ {tc('About')}", callback_data="u:about")]]
    line = []
    if config.UPDATES_LINK:
        line.append(IKB(f"⚑ {tc('Updates')}", url=config.UPDATES_LINK))
    if config.SUPPORT_LINK:
        line.append(IKB(f"✿ {tc('Support')}", url=config.SUPPORT_LINK))
    if line:
        rows.append(line)
    if is_adm:
        rows.append([IKB(f"⚙️ {tc('Admin Panel')}", callback_data="ap:home")])
    return IKM(rows)


def fsub_join_kb(channels, code=""):
    rows = []
    for c in channels:
        label = f"⚑ {tc('Join')} {c['title'][:22]}"
        if c.get("invite"):
            rows.append([IKB(label, url=c["invite"])])
    rows.append([IKB(f"↻ {tc('Try Again')}", callback_data=f"fs:retry:{code}")])
    return IKM(rows)


def close_only():
    return IKM([[IKB(f"✕ {tc('Close')}", callback_data="ap:close")]])
