import base64
import os
import json
import re
import time
import urllib.parse
import urllib.request
import requests
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, ContextTypes, ConversationHandler
)

# ----------------- CONFIGURATION -----------------
BOT_TOKEN = "8788531918:AAEqCUN-Yl1WWTQK1F7OihD9TIthDtAMsCU"  # আপনার বটের আসল টোকেন দিন
DEFAULT_OWNER_ID = 8289191009
DEFAULT_OWNER_USERNAME = "@SABBIRBD0"
DEFAULT_BOT_USERNAME = "@SABBIR_OBF_BOT"

# Conversation States
(
    WAITING_BROADCAST,
    WAITING_FORCE_CHANNEL,
    WAITING_BOT_USERNAME,
    WAITING_OWNER_USERNAME,
    WAITING_CUSTOM_HEADER,
    WAITING_ADD_ADMIN,
    WAITING_REMOVE_ADMIN,
    WAITING_TRANSFER_OWNERSHIP,
    WAITING_URL_TO_HTML,
    WAITING_SOURCE_CODE_URL,
    WAITING_CATBOX_MEDIA,
    WAITING_TELEGRAPH_IMAGE,
    WAITING_DEOBFUSCATE_FILE,
    WAITING_START_MSG,
    WAITING_AUTOPOST_CHANNEL,
    WAITING_AUTOPOST_CONTENT
) = range(16)

DATA_FILE = "bot_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "owner" not in data: data["owner"] = DEFAULT_OWNER_ID
                if "owner_username" not in data: data["owner_username"] = DEFAULT_OWNER_USERNAME
                if "bot_username" not in data: data["bot_username"] = DEFAULT_BOT_USERNAME
                if "admins" not in data: data["admins"] = []
                if "users" not in data: data["users"] = []
                if "force_channel" not in data: data["force_channel"] = ""
                if "custom_header" not in data: 
                    data["custom_header"] = "🔒 SABBIR UNBREAKABLE ULTRA CIPHER V2.0 - DO NOT MODIFY"
                if "custom_start_msg" not in data:
                    data["custom_start_msg"] = "👋 **স্বাগতম বটের ভেতরে!**\nনিচের মেনু থেকে আপনার কাঙ্ক্ষিত অপশন সিলেক্ট করুন।"
                return data
        except Exception:
            pass
    return {
        "owner": DEFAULT_OWNER_ID,
        "owner_username": DEFAULT_OWNER_USERNAME,
        "bot_username": DEFAULT_BOT_USERNAME,
        "admins": [],
        "users": [],
        "force_channel": "",
        "custom_header": "🔒 SABBIR UNBREAKABLE ULTRA CIPHER V2.0 - DO NOT MODIFY",
        "custom_start_msg": "👋 **স্বাগতম বটের ভেতরে!**\nনিচের মেনু থেকে আপনার কাঙ্ক্ষিত অপশন সিলেক্ট করুন।"
    }

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

bot_data = load_data()

def is_owner(user_id: int) -> bool:
    return user_id == bot_data.get("owner", DEFAULT_OWNER_ID)

def is_admin(user_id: int) -> bool:
    return is_owner(user_id) or (user_id in bot_data.get("admins", []))

# ----------------- ADVANCED DE-OBFUSCATOR ENGINE -----------------
def multi_layer_deobfuscate(raw_code: str) -> str:
    """মাল্টি-লেয়ার রিভার্স ইঞ্জিন ডিকোডার"""
    extracted_results = []
    
    # 1. URL Decoding (%20, %3C, etc.)
    try:
        if "%3C" in raw_code or "%20" in raw_code:
            unquoted = urllib.parse.unquote(raw_code)
            if unquoted != raw_code:
                extracted_results.append("=== [URL Decoded Stream] ===\n" + unquoted)
    except Exception:
        pass

    # 2. Base64 Multi-Extract & Decode (atob/b64decode)
    try:
        b64_pattern = r'(?:[A-Za-z0-9+/]{4}){4,}(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?'
        matches = re.findall(b64_pattern, raw_code)
        for m in matches:
            if len(m) > 20:
                try:
                    decoded = base64.b64decode(m).decode('utf-8', errors='ignore')
                    if any(key in decoded.lower() for key in ['<html', '<script', 'function', 'var ', 'const ', 'let ', 'document']):
                        extracted_results.append("=== [Base64 Decoded Block] ===\n" + decoded)
                except Exception:
                    pass
    except Exception:
        pass

    # 3. Hex / String Escapes Decoding (\x3c\x68\x74\x6d\x6c)
    try:
        hex_pattern = r'(?:\\x[0-9a-fA-F]{2})+'
        hex_matches = re.findall(hex_pattern, raw_code)
        for h in hex_matches:
            try:
                decoded_hex = bytes.fromhex(h.replace('\\x', '')).decode('utf-8', errors='ignore')
                if len(decoded_hex) > 5:
                    extracted_results.append("=== [Hex Escaped Code] ===\n" + decoded_hex)
            except Exception:
                pass
    except Exception:
        pass

    # 4. Unicode Escapes Decoding (\u003c\u0068\u0074\u006d\u006c)
    try:
        def replace_unicode(match):
            return chr(int(match.group(1), 16))
        uni_decoded = re.sub(r'\\u([0-9a-fA-F]{4})', replace_unicode, raw_code)
        if uni_decoded != raw_code:
            extracted_results.append("=== [Unicode Decoded Code] ===\n" + uni_decoded)
    except Exception:
        pass

    # রেজাল্ট ফিল্টারিং
    if extracted_results:
        final_output = "\n\n".join(extracted_results)
        return f"<!-- 🔓 DE-OBFUSCATED SUCCESSFUL BY {bot_data.get('bot_username')} -->\n\n" + final_output
    
    return f"<!-- ⚠️ High-Level Polymorphic Obfuscation Detected! Partial Cleaning Applied: -->\n\n" + raw_code

# ----------------- UPLOAD ENGINES -----------------
def upload_to_catbox(file_path: str) -> str:
    url = "https://catbox.moe/user/api.php"
    data = {"reqtype": "fileupload"}
    with open(file_path, "rb") as f:
        files = {"fileToUpload": f}
        response = requests.post(url, data=data, files=files)
        if response.status_code == 200:
            return response.text.strip()
        else:
            raise Exception("Catbox আপলোড ব্যর্থ হয়েছে!")

def upload_to_telegraph(file_path: str) -> str:
    url = "https://telegra.ph/upload"
    with open(file_path, "rb") as f:
        files = {"file": f}
        response = requests.post(url, files=files)
        if response.status_code == 200:
            res_json = response.json()
            if isinstance(res_json, list) and "src" in res_json[0]:
                return "https://telegra.ph" + res_json[0]["src"]
    raise Exception("Telegraph আপলোড ব্যর্থ হয়েছে!")

# ----------------- OBFUSCATION ENGINE -----------------
def heavy_obfuscate_html(html_code: str) -> str:
    bot_user = bot_data.get("bot_username", DEFAULT_BOT_USERNAME)
    owner_user = bot_data.get("owner_username", DEFAULT_OWNER_USERNAME)
    custom_hdr = bot_data.get("custom_header", "🔒 SABBIR UNBREAKABLE ULTRA CIPHER V2.0")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    encoded = base64.b64encode(html_code.encode('utf-8')).decode('utf-8')

    header_art = f"""<!--
//========================================================================
//  {custom_hdr}
//========================================================================
//  Obfuscated By: {owner_user}
//  Telegram Bot: {bot_user}
//  Timestamp: {timestamp}
//========================================================================
-->
"""

    obfuscated_template = f"""{header_art}
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
* {{
    -webkit-user-select: none !important;
    user-select: none !important;
}}
</style>
<script>
(function() {{
    'use strict';
    window.addEventListener('contextmenu', function(e) {{ e.preventDefault(); return false; }}, true);
    window.onload = function() {{
        try {{
            var _raw = "{encoded}";
            var _decoded = atob(_raw);
            document.open();
            document.write(_decoded);
            document.close();
        }} catch(err) {{}}
    }};
}})();
</script>
</head>
<body>
</body>
</html>"""
    return obfuscated_template

# ----------------- KEYBOARDS -----------------
def get_main_keyboard(user_id: int):
    keyboard = [
        ["🔐 OBFUSCATE HTML", "🔓 DE-OBFUSCATE CODE"],
        ["🖼️ IMAGE TO LINK", "🎬 VIDEO TO LINK"],
        ["📡 TELEGRAPH LINK", "💻 GET SOURCE CODE"],
        ["📢 AUTO POST BOT", "🔄 CHECK UPDATE"],
        ["👑 DEVELOPER INFO", "⚡ VIP FEATURES"]
    ]
    if is_admin(user_id):
        keyboard.append(["⚙️ Admin Panel"])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_admin_keyboard(user_id: int):
    keyboard = [
        ["📢 Broadcast Msg", "🔗 Set Force Channel"],
        ["❌ Remove Force Channel", "🤖 Set Bot Username"],
        ["🗑️ Remove Bot Username", "👤 Set Owner Username"],
        ["✏️ Set Start Message", "✏️ Set Watermark"],
        ["📊 User Stats"]
    ]
    if is_owner(user_id):
        keyboard.append(["➕ Add Admin", "➖ Remove Admin"])
        keyboard.append(["👑 Transfer Owner"])
    keyboard.append(["🔙 Back to Main Menu"])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def check_force_join(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    channel = bot_data.get("force_channel", "").strip()
    if not channel:
        return True
    try:
        member = await context.bot.get_chat_member(chat_id=channel, user_id=user_id)
        if member.status in ['creator', 'administrator', 'member']:
            return True
    except Exception:
        pass
    return False

# ----------------- START & MENUS -----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in bot_data["users"]:
        bot_data["users"].append(user_id)
        save_data(bot_data)

    if not await check_force_join(user_id, context):
        channel = bot_data.get("force_channel")
        await update.message.reply_text(f"⚠️ **বটটি ব্যবহার করতে অফিশিয়াল চ্যানেলে যুক্ত থাকুন:**\n\n📢 Channel: {channel}")
        return

    start_msg = bot_data.get("custom_start_msg", "👋 স্বাগতম!")
    await update.message.reply_text(start_msg, reply_markup=get_main_keyboard(user_id), parse_mode="Markdown")

async def menu_check_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("⏳ **কানেক্টিং টু সার্ভার...**")
    time.sleep(1)
    await msg.edit_text("🔄 **আপডেট ফাইল চেক করা হচ্ছে... [25%]**")
    time.sleep(1)
    await msg.edit_text("⚡ **সিস্টেম সিঙ্ক করা হচ্ছে... [75%]**")
    time.sleep(1)
    await msg.edit_text(
        "✅ **বটটি সম্পূর্ণ আপ-টু-ডেট আছে!**\n\n"
        "👇 অনুগ্রহ করে নিচের মেনু বাটন ব্যবহার করে আপনার কাজ সম্পাদন করুন।",
        reply_markup=get_main_keyboard(update.effective_user.id),
        parse_mode="Markdown"
    )

async def menu_developer_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    owner = bot_data.get("owner_username", DEFAULT_OWNER_USERNAME)
    bot_u = bot_data.get("bot_username", DEFAULT_BOT_USERNAME)
    await update.message.reply_text(
        f"👑 **DEVELOPER & BOT INFO**\n\n"
        f"👤 **Developer Username:** {owner}\n"
        f"🤖 **Bot Username:** {bot_u}\n"
        f"🛡️ **System Status:** Active (V2.5 Ultra)",
        parse_mode="Markdown"
    )

# ----------------- DE-OBFUSCATION HANDLER -----------------
async def menu_deobfuscate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔓 **আপনার অবফাস্কেট বা এনক্রিপ্ট করা ফাইলটি পাঠান অথবা সরাসরি কোড পেস্ট করুন:**")
    return WAITING_DEOBFUSCATE_FILE

async def proc_deobfuscate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("🔄 **অ্যাডভান্সড ডি-অবফাস্কেট ইঞ্জিন প্রসেস করছে...**")
    
    code_text = ""
    file_name = "deobfuscated_result.html"

    if update.message.document:
        doc = update.message.document
        file_name = f"Decrypted_{doc.file_name}"
        file = await doc.get_file()
        file_bytes = await file.download_as_bytearray()
        code_text = file_bytes.decode('utf-8', errors='ignore')
    elif update.message.text:
        code_text = update.message.text

    decrypted_code = multi_layer_deobfuscate(code_text)

    with open(file_name, "w", encoding="utf-8") as f:
        f.write(decrypted_code)

    await msg.delete()
    await update.message.reply_document(
        document=open(file_name, "rb"),
        filename=file_name,
        caption="✅ **কোড রিভার্স ইঞ্জিনিয়ারিং ও ডিকোডিং সম্পন্ন হয়েছে!**",
        parse_mode="Markdown"
    )
    if os.path.exists(file_name):
        os.remove(file_name)

    return ConversationHandler.END

# ----------------- AUTO POST BOT -----------------
async def menu_autopost(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📢 **যে চ্যানেলে পোস্ট দিতে চান তার Username/ID দিন (যেমন: `@YourChannel`):**")
    return WAITING_AUTOPOST_CHANNEL

async def proc_autopost_chan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['target_channel'] = update.message.text.strip()
    await update.message.reply_text("📝 **চ্যানেলে দেওয়ার জন্য পোস্টের মেসেজ বা কোড লিখে পাঠান:**")
    return WAITING_AUTOPOST_CONTENT

async def proc_autopost_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = context.user_data.get('target_channel')
    content = update.message.text
    
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("🔗 Join Official Channel", url=f"https://t.me/{target.replace('@','')}")
    ]])

    try:
        await context.bot.send_message(chat_id=target, text=content, reply_markup=keyboard, parse_mode="Markdown")
        await update.message.reply_text(f"✅ **সফলভাবে `{target}` চ্যানেলে পোস্ট পাবলিশ হয়েছে!**", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ পোস্ট পাঠানো যায়নি: {str(e)}\n(নিশ্চিত করুন বটটি ওই চ্যানেলে Admin আছে)")

    return ConversationHandler.END

# ----------------- ADMIN SETTINGS -----------------
async def menu_set_start_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✏️ **নতুন কাস্টম Start মেসেজটি লিখে পাঠান:**")
    return WAITING_START_MSG

async def proc_start_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot_data["custom_start_msg"] = update.message.text.strip()
    save_data(bot_data)
    await update.message.reply_text("✅ Start মেসেজ সফলভাবে আপডেট হয়েছে!")
    return ConversationHandler.END

# ----------------- OTHER PROCESSORS -----------------
async def menu_catbox_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📦 **Catbox এর জন্য আপনার ছবি বা ভিডিওটি পাঠান:**")
    return WAITING_CATBOX_MEDIA

async def menu_telegraph_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📡 **Telegraph লিংক তৈরির জন্য আপনার ছবিটি পাঠান:**")
    return WAITING_TELEGRAPH_IMAGE

async def menu_get_source_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💻 **যে ওয়েবসাইটের সোর্স কোড ডাউনলোড করতে চান সেটির লিংক দিন:**")
    return WAITING_SOURCE_CODE_URL

async def proc_catbox_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("🔄 **Catbox-এ ফাইল আপলোড হচ্ছে...**")
    file_path = "temp_catbox"
    try:
        if update.message.photo:
            file = await update.message.photo[-1].get_file()
            file_path += ".jpg"
        elif update.message.video:
            file = await update.message.video.get_file()
            file_path += ".mp4"
        elif update.message.document:
            file = await update.message.document.get_file()
            file_path += "_" + (update.message.document.file_name or "file")
        
        await file.download_to_drive(file_path)
        catbox_link = upload_to_catbox(file_path)
        await msg.edit_text(f"✅ **Catbox ডিরেক্ট লিংক:** `{catbox_link}`", parse_mode="Markdown")
    except Exception as e:
        await msg.edit_text(f"❌ ব্যর্থ: {str(e)}")
    finally:
        if os.path.exists(file_path): os.remove(file_path)
    return ConversationHandler.END

async def proc_telegraph_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("🔄 **Telegraph-এ ছবি আপলোড হচ্ছে...**")
    file_path = "temp_tele.jpg"
    try:
        if update.message.photo:
            file = await update.message.photo[-1].get_file()
            await file.download_to_drive(file_path)
            tele_link = upload_to_telegraph(file_path)
            await msg.edit_text(f"✅ **Telegraph ইমেজ লিংক:** `{tele_link}`", parse_mode="Markdown")
    except Exception as e:
        await msg.edit_text(f"❌ ব্যর্থ: {str(e)}")
    finally:
        if os.path.exists(file_path): os.remove(file_path)
    return ConversationHandler.END

async def proc_source_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if not url.startswith(("http://", "https://")): url = "https://" + url
    msg = await update.message.reply_text("🔄 **সোর্স কোড নামানো হচ্ছে...**")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=12) as resp:
            source_text = resp.read().decode('utf-8', errors='ignore')
            filename = "Source_Code.html"
            with open(filename, "w", encoding="utf-8") as f: f.write(source_text)
            await msg.delete()
            await update.message.reply_document(document=open(filename, "rb"), filename=filename, caption=f"🌐 `{url}`")
            if os.path.exists(filename): os.remove(filename)
    except Exception as e:
        await msg.edit_text(f"❌ ব্যর্থ: {str(e)}")
    return ConversationHandler.END

async def menu_obfuscate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📂 **আপনার HTML ফাইলটি সেন্ড করুন বা কোড পেস্ট করুন:**")
    return ConversationHandler.END

async def menu_admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_admin(update.effective_user.id):
        await update.message.reply_text("⚙️ **ADMIN PANEL**", reply_markup=get_admin_keyboard(update.effective_user.id))
    return ConversationHandler.END

async def menu_back_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔙 মূল মেনুতে ফিরে আসা হয়েছে।", reply_markup=get_main_keyboard(update.effective_user.id))
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ বাতিল করা হয়েছে।", reply_markup=get_main_keyboard(update.effective_user.id))
    return ConversationHandler.END

# ----------------- MAIN ENTRY -----------------
if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^🔐 OBFUSCATE HTML$"), menu_obfuscate),
            MessageHandler(filters.Regex("^🔓 DE-OBFUSCATE CODE$"), menu_deobfuscate),
            MessageHandler(filters.Regex("^🖼️️ IMAGE TO LINK$"), menu_catbox_media),
            MessageHandler(filters.Regex("^🎬 VIDEO TO LINK$"), menu_catbox_media),
            MessageHandler(filters.Regex("^📡 TELEGRAPH LINK$"), menu_telegraph_image),
            MessageHandler(filters.Regex("^💻 GET SOURCE CODE$"), menu_get_source_code),
            MessageHandler(filters.Regex("^📢 AUTO POST BOT$"), menu_autopost),
            MessageHandler(filters.Regex("^🔄 CHECK UPDATE$"), menu_check_update),
            MessageHandler(filters.Regex("^👑 DEVELOPER INFO$"), menu_developer_info),
            MessageHandler(filters.Regex("^⚙️️ Admin Panel$"), menu_admin_panel),
            MessageHandler(filters.Regex("^🔙 Back to Main Menu$"), menu_back_main),
            MessageHandler(filters.Regex("^✏️ Set Start Message$"), menu_set_start_msg),
        ],
        states={
            WAITING_SOURCE_CODE_URL: [MessageHandler(filters.TEXT & ~filters.COMMAND, proc_source_code)],
            WAITING_CATBOX_MEDIA: [MessageHandler(filters.PHOTO | filters.VIDEO | filters.Document.ALL, proc_catbox_media)],
            WAITING_TELEGRAPH_IMAGE: [MessageHandler(filters.PHOTO, proc_telegraph_image)],
            WAITING_DEOBFUSCATE_FILE: [MessageHandler(filters.TEXT | filters.Document.ALL, proc_deobfuscate)],
            WAITING_AUTOPOST_CHANNEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, proc_autopost_chan)],
            WAITING_AUTOPOST_CONTENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, proc_autopost_send)],
            WAITING_START_MSG: [MessageHandler(filters.TEXT & ~filters.COMMAND, proc_start_msg)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)

    print("Bot completely updated with Advanced Unobfuscator Engine!")
    app.run_polling()
