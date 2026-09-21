"""
Saare inline keyboards — coloured buttons (kurigram ButtonStyle) + stylish fonts.

Colour scheme (screenshot jaisa):
  🔵 blue  = normal / info actions
  🟢 green = positive (done, approve, broadcast, backup)
  🔴 red   = destructive / warning (ban, revoke, close, maintenance)
"""
from pyrogram.types import InlineKeyboardMarkup as IKM

import database as db
from utils.buttons import blue, green, grey, red
from utils.fonts import tc


def _sync_colors():
    """DB se colour toggle padho."""
    from utils import buttons as B
    B.set_colors(db.get_bool("colors", True))


# ───────────────────────────── ADMIN PANEL ─────────────────────────────
def admin_panel(user_id=0):
    _sync_colors()
    ad_on = db.get_bool("auto_delete_on", True)
    pr_on = db.get_bool("protect")
    fs_on = db.get_bool("force_sub")
    mt_on = db.get_bool("maintenance")

    def toggle_btn(label, key, on, default_green=True):
        txt = f"{'✓' if on else '✘'} {tc(label)}: {'ᴏɴ' if on else 'ᴏғғ'}"
        fn = green if on else red
        if not default_green:
            fn = red if on else grey
        return fn(txt, callback_data=f"tg:{key}")

    rows = [
        [blue(f"▪️ {tc('Stats')}", callback_data="ap:stats"),
         blue(f"◉ {tc('Users')}", callback_data="ap:users")],

        [blue(f"◆ {tc('All Files')}", callback_data="ap:files"),
         blue(f"◆ {tc('Batches')}", callback_data="ap:batches")],

        [green(f"⚑ {tc('Broadcast')}", callback_data="ap:bc"),
         red(f"✘ {tc('Ban / Unban')}", callback_data="ap:ban")],

        [green(f"⊕ {tc('Add Admin')}", callback_data="ap:addadmin"),
         blue(f"◇ {tc('Admins')}", callback_data="ap:admins")],

        [blue(f"❖ {tc('Auto Delete')}", callback_data="ap:autodel"),
         blue(f"✿ {tc('Protect')}", callback_data="ap:protect")],

        [blue(f"⚑ {tc('Force Sub')}", callback_data="ap:fsub"),
         blue(f"◉ {tc('Audit Log')}", callback_data="ap:logs")],

        [green(f"💾 {tc('Backup Db')}", callback_data="ap:backup"),
         red(f"▣ {tc('Security')}", callback_data="ap:sec")],

        [red(f"⚠️ {tc('Maintenance')}", callback_data="ap:maint"),
         blue(f"⚙️ {tc('Settings')}", callback_data="ap:settings")],

        [toggle_btn("Auto Del", "auto_delete_on", ad_on),
         toggle_btn("Protect", "protect", pr_on)],

        [toggle_btn("F-Sub", "force_sub", fs_on),
         toggle_btn("Maint", "maintenance", mt_on, default_green=False)],

        [blue(f"▲ {tc('Start Photo')}", callback_data="ap:photo"),
         green(f"↻ {tc('Restart')}", callback_data="ap:restart")],

        [blue(f"✦ {tc('System')}", callback_data="ap:system"),
         green(f"👨‍💻 {tc('Developer')}", callback_data="u:dev")],

        [red(f"✕ {tc('Close')}", callback_data="ap:close")],
    ]
    return IKM(rows)


def back(to="ap:home", extra=None):
    _sync_colors()
    rows = list(extra) if extra else []
    rows.append([grey(f"« {tc('Back')}", callback_data=to),
                 red(f"✕ {tc('Close')}", callback_data="ap:close")])
    return IKM(rows)


# ───────────────────────────── SUB MENUS ─────────────────────────────
def stats_kb():
    return back(extra=[[green(f"↻ {tc('Refresh')}", callback_data="ap:stats"),
                        blue(f"✦ {tc('System')}", callback_data="ap:system")]])


def users_kb():
    return back(extra=[
        [blue(f"◉ {tc('Recent')}", callback_data="ap:users"),
         red(f"✘ {tc('Banned')}", callback_data="ap:banned")],
        [green(f"⚑ {tc('Export Ids')}", callback_data="ap:export")],
    ])


def files_kb():
    return back(extra=[[blue(f"◆ {tc('Recent')}", callback_data="ap:files"),
                        green(f"★ {tc('Top Opened')}", callback_data="ap:topfiles")]])


def autodel_kb():
    _sync_colors()
    cur = db.get_int("auto_delete", 1800)
    opts = [("10 ᴍɪɴ", 600), ("30 ᴍɪɴ", 1800), ("1 ʜᴏᴜʀ", 3600),
            ("6 ʜᴏᴜʀs", 21600), ("24 ʜᴏᴜʀs", 86400), ("ᴏғғ", 0)]
    rows, line = [], []
    for label, val in opts:
        if val == cur:
            b = green(f"✅ {label}", callback_data=f"set:auto_delete:{val}")
        elif val == 0:
            b = red(label, callback_data=f"set:auto_delete:{val}")
        else:
            b = blue(label, callback_data=f"set:auto_delete:{val}")
        line.append(b)
        if len(line) == 3:
            rows.append(line)
            line = []
    if line:
        rows.append(line)
    return back(extra=rows)


def confirm_kb(action, arg=""):
    _sync_colors()
    return IKM([[green(f"✓ {tc('Yes')}", callback_data=f"ok:{action}:{arg}"),
                 red(f"✘ {tc('No')}", callback_data="ap:home")]])


def bc_kb():
    return back(extra=[[green(f"⚑ {tc('All Users')}", callback_data="bc:all"),
                        red(f"✘ {tc('Cancel')}", callback_data="ap:home")]])


def fsub_kb():
    _sync_colors()
    rows = []
    for ch in db.fsub_list():
        rows.append([red(f"✘ {tc('Remove')}: {ch['title'][:18]}",
                         callback_data=f"fsub:rm:{ch['chat_id']}")])
    return back(extra=rows)


def admins_kb():
    _sync_colors()
    import config
    rows = []
    for uid in db.admin_ids():
        if uid == config.OWNER_ID:
            rows.append([green(f"★ {uid} ({tc('Owner')})", callback_data="noop")])
        else:
            rows.append([red(f"✘ {tc('Remove')} {uid}", callback_data=f"adm:rm:{uid}")])
    return back(extra=rows)


# ───────────────────────────── BATCH FLOW ─────────────────────────────
def batch_collect_kb(count=0):
    _sync_colors()
    return IKM([
        [green(f"✓ {tc('Done')} ({count})", callback_data="batch:done")],
        [blue(f"↺ {tc('Clear')}", callback_data="batch:clear"),
         red(f"✘ {tc('Cancel')}", callback_data="batch:cancel")],
    ])


def link_kb(link, code):
    _sync_colors()
    return IKM([
        [green(f"▸ {tc('Open Link')}", url=link)],
        [blue(f"⚑ {tc('Share')}", url=f"https://t.me/share/url?url={link}")],
        [red(f"✘ {tc('Revoke')}", callback_data=f"lnk:rv:{code}"),
         blue(f"◉ {tc('Info')}", callback_data=f"lnk:in:{code}")],
    ])


# ───────────────────────────── USER SIDE ─────────────────────────────
def start_kb(is_adm=False):
    _sync_colors()
    import config
    rows = [[blue(f"◈ {tc('How To Use')}", callback_data="u:help"),
             blue(f"◉ {tc('About')}", callback_data="u:about")],
            [green(f"👨‍💻 {tc('Developer')}", callback_data="u:dev")]]
    line = []
    if config.UPDATES_LINK:
        line.append(green(f"⚑ {tc('Updates')}", url=config.UPDATES_LINK))
    if config.SUPPORT_LINK:
        line.append(blue(f"✿ {tc('Support')}", url=config.SUPPORT_LINK))
    if line:
        rows.append(line)
    if is_adm:
        rows.append([green(f"⚙️ {tc('Admin Panel')}", callback_data="ap:home")])
    return IKM(rows)


def fsub_join_kb(channels, code=""):
    _sync_colors()
    rows = []
    for c in channels:
        label = f"⚑ {tc('Join')} {c['title'][:22]}"
        if c.get("invite"):
            rows.append([blue(label, url=c["invite"])])
    rows.append([green(f"↻ {tc('Try Again')}", callback_data=f"fs:retry:{code}")])
    return IKM(rows)


def dev_kb():
    """Developer section — portfolio link ke saath."""
    _sync_colors()
    from pyrogram.types import InlineKeyboardMarkup
    return InlineKeyboardMarkup([
        [green("🌐 ᴠɪsɪᴛ ᴘᴏʀᴛғᴏʟɪᴏ", url="https://new-profotilo-flame.vercel.app")],
        [blue("✉️ ᴇᴍᴀɪʟ", url="mailto:harsh48227@gmail.com"),
         blue("💼 ʜɪʀᴇ ᴍᴇ", url="https://tally.so/r/QKpNqX")],
        [grey(f"« {tc('Back')}", callback_data="u:home")],
    ])


def close_only():
    _sync_colors()
    return IKM([[red(f"✕ {tc('Close')}", callback_data="ap:close")]])


def get_again_kb():
    """Auto-delete ke baad 'dobara chahiye' button."""
    _sync_colors()
    return IKM([[green(f"↻ {tc('Get Files Again')}", callback_data="noop")]])
