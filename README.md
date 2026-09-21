# 🤖 Harsh File Store Bot v1.0

Telegram **File Store Bot** — batch me videos bhejo, ek link milta hai, koi bhi user us link se bot start kare to saari files usko mil jaati hain aur **30 minute baad auto-delete** ho jaati hain.

Storage: **SQLite on Railway Volume** (`/data`) — redeploy pe data safe rehta hai.

---

## 📋 Flow (jaisa tumne bataya)

```
ADMIN                                    USER
─────                                    ────
/batch                                   
  ↓                                      
video 1, video 2, video 3...             
  ↓ (bot DB channel me save karta hai)   
/done                                    
  ↓                                      
🔗 https://t.me/YourBot?start=Ab3xK9pQ2   
  └──────── link share ──────────────→   link click
                                            ↓
                                         START dabaya
                                            ↓
                                         saari videos aa gayi
                                            ↓
                                         ⚠️ "30 min me delete — forward kar lo"
                                            ↓ (30 min)
                                         🗑 sab delete
```

---

## ⚙️ Railway Deploy (step by step)

### 1. Pehle ye 3 cheezein bana lo

| Kya | Kahan se |
|---|---|
| `API_ID` + `API_HASH` | [my.telegram.org](https://my.telegram.org) → API development tools |
| `BOT_TOKEN` | [@BotFather](https://t.me/BotFather) → `/newbot` |
| `DB_CHANNEL` | Ek **private channel** banao → bot ko **admin** banao → channel me koi msg forward karke `/id` se ID lo (`-100...` se start hoti hai) |

### 2. Railway par project banao

1. GitHub pe ye folder push karo
2. Railway → **New Project → Deploy from GitHub repo**
3. Repo select karo → deploy start ho jayega

### 3. ⭐ Volume mount karo (SABSE ZAROORI)

Railway service → **Settings** → **Volumes** → **+ New Volume**

```
Mount Path:  /data
Size:        1 GB (free tier me kaafi hai)
```

> Volume mount **nahi** kiya to har redeploy pe users/links sab udd jayenge.

> ℹ️ Dockerfile me `VOLUME` instruction **nahi** hai — Railway usse reject karta hai.
> Volume sirf dashboard se add hota hai (upar wale steps).

### 4. Variables tab me daalo

```env
API_ID=123456
API_HASH=abcdef1234567890abcdef
BOT_TOKEN=7123456789:AAE...
OWNER_ID=1234567890
DB_CHANNEL=-1001234567890
LOG_CHANNEL=-1001234567890
DATA_DIR=/data
AUTO_DELETE=1800
BOT_NAME=Harsh File Store Bot
PORT=8080
```

**Optional:**
```env
ADMINS=111111 222222        # extra admins (space/comma se)
PROTECT_CONTENT=false       # true = user forward nahi kar payega
FORCE_SUB=false
START_PHOTO=https://...jpg
SUPPORT_LINK=https://t.me/...
UPDATES_LINK=https://t.me/...
```

### 5. Deploy → logs me dekho

```
DB channel ready: My Storage
🌐 health server on :8080
🤖 @YourBot live · data dir: /data
```

Bas ho gaya. Bot ko `/start` bhejo.

---

## 🎮 Commands

### Admin
| Command | Kaam |
|---|---|
| `/batch` | Batch mode ON — ab videos bhejo |
| `/done` | Batch khatam → link milega |
| `/cancel` | Batch cancel |
| `/link` | Single file ka link (reply karke) |
| `/panel` | Full admin panel |
| `/stats` | Statistics |
| `/broadcast` | Sab users ko msg (reply karke) |
| `/ban 12345 reason` | User ban |
| `/unban 12345` | Unban |
| `/banned` | Banned list |
| `/addadmin 12345` | Naya admin (sirf owner) |
| `/rmadmin 12345` | Admin hatao (sirf owner) |
| `/admins` | Admin list |
| `/autodel 1800` | Auto-delete time (seconds, 0 = off) |
| `/addfsub -100xxx` | Force-sub channel add |
| `/backup` | DB file bhejo |
| `/revoke <code>` | Link band karo |
| `/restart` | Bot restart |
| `/id` | ID nikalo |

### User
`/start` · `/help` — bas. Baaki sab link se chalta hai.

---

## 🎛 Admin Panel Buttons

```
▪️ Sᴛᴀᴛs            ◉ Usᴇʀs
◆ Aʟʟ Fɪʟᴇs         ◆ Bᴀᴛᴄʜᴇs
⚑ Bʀᴏᴀᴅᴄᴀsᴛ         ✘ Bᴀɴ / Uɴʙᴀɴ
⊕ Aᴅᴅ Aᴅᴍɪɴ         ◇ Aᴅᴍɪɴs
❖ Aᴜᴛᴏ Dᴇʟᴇᴛᴇ       ✿ Pʀᴏᴛᴇᴄᴛ
⚙️ Fᴏʀᴄᴇ Sᴜʙ        ◉ Aᴜᴅɪᴛ Lᴏɢ
⚙️ Bᴀᴄᴋᴜᴘ Dʙ        ▣ Sᴇᴄᴜʀɪᴛʏ
⚠️ Mᴀɪɴᴛᴇɴᴀɴᴄᴇ      ⚙️ Sᴇᴛᴛɪɴɢs
✓ Aᴜᴛᴏ Dᴇʟ: ᴏɴ      ✿ Pʀᴏᴛᴇᴄᴛ: ᴏғғ
⚑ F-Sᴜʙ: ᴏғғ        ⚠️ Mᴀɪɴᴛ: ᴏғғ
▲ Sᴛᴀʀᴛ Pʜᴏᴛᴏ       ↻ Rᴇsᴛᴀʀᴛ
✦ Sʏsᴛᴇᴍ            ✕ Cʟᴏsᴇ
```

Har button live hai — koi dummy nahi.

---

## 📁 File Structure

```
filestore-bot/
├── bot.py               # main client
├── config.py            # env vars + volume detect
├── database.py          # SQLite (users/batches/admins/logs/settings)
├── web.py               # Railway health check
├── handlers/
│   ├── start.py         # /start, deep link, file delivery, auto-delete
│   ├── batch.py         # /batch /done /link /revoke
│   ├── admin.py         # /panel /stats /ban /broadcast /backup...
│   └── callbacks.py     # saare inline buttons
├── utils/
│   ├── fonts.py         # sᴍᴀʟʟ ᴄᴀᴘs converter
│   ├── keyboards.py     # panel layouts
│   ├── texts.py         # saare messages
│   └── helpers.py       # size/time/code utils
├── Dockerfile           # Railway build
├── railway.json         # deploy config + healthcheck
├── Procfile
├── requirements.txt
└── .env.example
```

---

## 🔒 Security Features

- **Ban system** — banned user ko kuch nahi milta
- **Protect content** — ON karo to user forward/save nahi kar sakta
- **Force subscribe** — channel join zaroori
- **Revoke link** — purana link turant dead
- **Maintenance mode** — sirf admin use kar sakta
- **Audit log** — kisne kya kiya sab record
- **Owner-only** — addadmin/rmadmin/backup/restart sirf owner ke liye

---

## ❓ Common Problems

**"DB_CHANNEL error"** → bot ko us channel me admin banao (post messages permission ke saath)

**Redeploy pe data gaya** → Volume mount path `/data` hai ya nahi check karo, aur `DATA_DIR=/data` variable set hai ya nahi

**Files nahi aa rahi** → DB channel se messages delete mat karo, bot wahi se copy karta hai

**Force sub kaam nahi kar raha** → bot ko us channel me bhi admin banao
