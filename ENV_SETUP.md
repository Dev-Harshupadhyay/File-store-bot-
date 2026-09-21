# 🔐 Railway Environment Variables — Setup Guide

## ⚠️ PEHLE YE PADHO (Security)

Credentials kabhi bhi chat / screenshot / public repo me mat daalo.
Agar galti se leak ho jaye to turant revoke karo:

1. [@BotFather](https://t.me/BotFather) → `/mybots` → apna bot chuno
2. **API Token** → **Revoke current token**
3. Naya token copy karo → Railway variables me `BOT_TOKEN` update karo

Ye saari values sirf **Railway → Variables** me daalni hain, kabhi code me hardcode mat karna.
`railway-env.json` `.gitignore` me hai — wo kabhi commit nahi hoga.

---

## 📋 Railway me kaise daalein

### Method 1 — Raw JSON Editor (sabse fast)

1. Railway → apni service → **Variables** tab
2. Upar right me **Raw Editor** dabao
3. Format **JSON** select karo
4. `railway-env.json` ka poora content paste karo
5. **Save** → service auto redeploy hogi

### Method 2 — Ek ek karke

Variables tab → **+ New Variable** → neeche wali table se add karo.

---

## 🔑 Variables Table

| Key | Value | Zaroori? |
|---|---|---|
| `API_ID` | `your_api_id` | ✅ haan |
| `API_HASH` | `your_api_hash` | ✅ haan |
| `BOT_TOKEN` | `your_bot_token` | ✅ haan |
| `OWNER_ID` | `your_telegram_id` | ✅ haan |
| `ADMINS` | `your_telegram_id` | ❌ optional |
| `DB_CHANNEL` | `-100xxxxxxxxxx` | ✅ **haan — ye abhi missing hai** |
| `LOG_CHANNEL` | `-100xxxxxxxxxx` | ❌ optional (default = DB_CHANNEL) |
| `DATA_DIR` | `/data` | ✅ haan (volume) |
| `AUTO_DELETE` | `1800` | ❌ optional (30 min) |
| `PROTECT_CONTENT` | `false` | ❌ optional |
| `FORCE_SUB` | `false` | ❌ optional |
| `BOT_NAME` | `Harsh File Store Bot` | ❌ optional |
| `PORT` | `8080` | ❌ optional |

---

## ❗ DB_CHANNEL kaise nikaalein (ye abhi baaki hai)

Bot bina iske **start nahi hoga**. Saari files yahi store hoti hain.

**Steps:**

1. Telegram me **New Channel** banao → **Private** rakho
   (naam kuch bhi: "Harsh FS Storage")
2. Channel → **Administrators** → **Add Admin** → apna bot `@...` search karke add karo
   - Permissions: **Post Messages** ✅, **Delete Messages** ✅ zaroor on rakhna
3. Channel ID nikaalne ke 2 tareeke:

   **Tareeka A (bot se):**
   - Channel me koi bhi message bhejo
   - Us message ko apne bot ko **forward** karo
   - Bot me `/id` likho → `◆ ᴄʜᴀɴɴᴇʟ ɪᴅ: -1001234567890` mil jayega

   **Tareeka B ([@username_to_id_bot](https://t.me/username_to_id_bot)):**
   - Channel ka message us bot ko forward karo → ID mil jayegi

4. Jo `-100...` wali ID mile, wo `DB_CHANNEL` aur `LOG_CHANNEL` dono me daal do

> ⚠️ Us channel se messages **kabhi delete mat karna** — bot wahi se copy karke user ko bhejta hai.

---

## 💾 Volume (mat bhoolna)

Railway service → **Settings** → **Volumes** → **+ New Volume**

```
Mount Path : /data
Size       : 1 GB
```

Volume ke bina har redeploy pe users + links sab udd jayenge.

---

## ✅ Deploy ke baad logs me ye dikhna chahiye

```
[11:50:12] INFO · bot · DB channel ready: Harsh FS Storage
[11:50:12] INFO · bot · 🌐 health server on :8080
[11:50:13] INFO · bot · 🤖 @YourBot live · data dir: /data
```

Agar ye aaya to sab sahi. Bot ko `/start` bhejo → admin panel dikhega.

### Error aaye to

| Error | Fix |
|---|---|
| `Missing env vars: DB_CHANNEL` | DB_CHANNEL variable set nahi hai |
| `DB_CHANNEL error: CHANNEL_INVALID` | Bot us channel me admin nahi hai |
| `AUTH_KEY_DUPLICATED` | Purana session — volume se `filestore.session` delete karo |
| `data dir: /app/data` (instead of `/data`) | Volume mount nahi hua |
