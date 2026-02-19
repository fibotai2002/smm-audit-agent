from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from bot.models import User, Audit
from bot.services.audit_engine import AuditEngine
from bot.services.user_service import UserService
from bot.services.gemini_service import GeminiService
from bot.services.chart_service import ChartService
from bot.services.pdf_service import ReportGenerator
from bot.services.formatter import Formatter
from bot.states import WAITING_FOR_INSTAGRAM, WAITING_FOR_TELEGRAM, WAITING_FOR_LIMIT
from django.conf import settings
from django.utils import timezone
from asgiref.sync import sync_to_async
from loguru import logger
import io

audit_engine = AuditEngine()
user_service = UserService()
gemini_service = GeminiService()

async def get_main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("🚀 Yangi Audit", callback_data="start_audit")],
        [InlineKeyboardButton("👤 Mening Hisobim", callback_data="my_profile"), InlineKeyboardButton("💎 Tariflar", callback_data="pricing")],
        [InlineKeyboardButton("🆘 Yordam", callback_data="help")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db_user, created = await user_service.get_or_create_user(user.id, user.username, user.full_name)
    
    if created:
        await update.message.reply_text(
            "🎉 **Xush kelibsiz!**\n\n"
            "Siz SMMind AI botiga muvaffaqiyatli qo'shildingiz.\n"
            "Bu bot orqali Instagram va Telegram profillaringizni sun'iy intellekt yordamida tahlil qilishingiz mumkin.\n\n"
            "👇 **Boshlash uchun 'Yangi Audit' tugmasini bosing!**",
            parse_mode="Markdown"
        )

    txt = (
        f"👋 **Salom, {user.full_name}!**\n\n"
        "Men **SMMind AI** - SMM Audit yordamchiningizman.\n"
        "Quyidagi menyudan kerakli bo'limni tanlang:"
    )
    await update.message.reply_text(txt, reply_markup=await get_main_menu_keyboard(), parse_mode="Markdown")

async def main_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    txt = "🏠 **Bosh Sahifa**\nKerakli bo'limni tanlang:"
    try:
        await query.message.edit_text(txt, reply_markup=await get_main_menu_keyboard(), parse_mode="Markdown")
    except Exception:
        await query.message.reply_text(txt, reply_markup=await get_main_menu_keyboard(), parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = (
        "🆘 **Yordam Markazi**\n\n"
        "1. **Audit qilish**: 'Yangi Audit' tugmasini bosing va Instagram/Telegram havolalarini yuboring.\n"
        "2. **Limitlar**: Free (1/kun), Pro (Cheksiz).\n"
        "3. **Muammo bo'lsa**: @fibotai ga yozing.\n\n"
        "📚 **Qo'llanma**: /tutorial"
    )
    keyboard = [
        [InlineKeyboardButton("📚 To'liq Qo'llanma", callback_data="tutorial")],
        [InlineKeyboardButton("⬅️ Ortga", callback_data="main_menu")]
    ]
    # Check if triggered via callback or command
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.message.edit_text(txt, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    else:
        await update.message.reply_text(txt, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def tutorial_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    txt = (
        "📚 **Qo'llanma**\n\n"
        "1️⃣ **Ro'yxatdan o'tish**: Siz allaqachon ro'yxatdan o'tgansiz.\n"
        "2️⃣ **Audit boshlash**: 'Yangi Audit' tugmasini bosing.\n"
        "3️⃣ **Link yuborish**: Avval Instagram, keyin Telegram kanal linkini yuboring (yoki /skip).\n"
        "4️⃣ **Natija**: Bot sizga 5-10 soniyada tahlil, xatolar va maslahatlarni beradi.\n"
        "5️⃣ **Pro**: Agar ko'proq imkoniyat kerak bo'lsa, /pricing bo'limidan Pro tarifini oling.\n\n"
        "Boshlashga tayyormisiz? 👇"
    )
    keyboard = [[InlineKeyboardButton("🚀 Boshlash (Audit)", callback_data="start_audit")], [InlineKeyboardButton("⬅️ Ortga", callback_data="help")]]
    await query.message.edit_text(txt, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def my_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    db_user = await user_service.get_user(user_id)
    
    # Calculate usage
    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    audit_count = await Audit.objects.filter(user=db_user, created_at__gte=today_start).acount()
    total_audits = await Audit.objects.filter(user=db_user).acount()
    
    tier_info = settings.TIERS.get(db_user.tier, settings.TIERS["free"])
    daily_limit = 1 if db_user.tier == "free" else "Cheksiz"
    
    txt = (
        f"👤 **Foydalanuvchi:** {db_user.full_name}\n"
        f"🆔 ID: `{user_id}`\n\n"
        f"💎 **Tarif:** {db_user.tier.upper()}\n"
        f"📊 **Bugungi Auditlar:** {audit_count} / {daily_limit}\n"
        f"📈 **Jami Auditlar:** {total_audits}\n"
        f"📅 **Obuna tugash vaqti:** {db_user.subscription_expires_at.strftime('%Y-%m-%d') if db_user.subscription_expires_at else 'Cheksiz'}\n"
    )
    
    keyboard = [
        [InlineKeyboardButton("💎 Tarifni o'zgartirish", callback_data="pricing")],
        [InlineKeyboardButton("⬅️ Ortga", callback_data="main_menu")]
    ]
    await query.message.edit_text(txt, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def start_audit_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    db_user, _ = await user_service.get_or_create_user(user_id, update.effective_user.username, update.effective_user.full_name)
    
    if db_user.tier == "free":
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        count = await Audit.objects.filter(user=db_user, created_at__gte=today_start).acount()
        if count >= 1:
            await query.message.reply_text(
                "❌ **Kunlik limit tugadi!**\nPRO ga o'ting: /pricing"
            )
            return ConversationHandler.END

    audit = await Audit.objects.acreate(user=db_user)
    context.user_data["audit_id"] = str(audit.id)
    context.user_data["user_tier"] = db_user.tier
    
    await query.message.reply_text("🔗 **Instagram** profilingiz linkini yuboring (yoki /skip):")
    return WAITING_FOR_INSTAGRAM

async def start_audit_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Wrapper for command-based trigger
    return await _start_audit_logic(update, context)

async def _start_audit_logic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    db_user, _ = await user_service.get_or_create_user(user_id, update.effective_user.username, update.effective_user.full_name)
    
    if db_user.tier == "free":
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        count = await Audit.objects.filter(user=db_user, created_at__gte=today_start).acount()
        if count >= 1:
            await update.message.reply_text(
                "❌ **Kunlik limit tugadi!**\nPRO ga o'ting: /pricing"
            )
            return ConversationHandler.END

    audit = await Audit.objects.acreate(user=db_user)
    context.user_data["audit_id"] = str(audit.id)
    context.user_data["user_tier"] = db_user.tier
    
    await update.message.reply_text("🔗 **Instagram** profilingiz linkini yuboring (yoki /skip):")
    return WAITING_FOR_INSTAGRAM

async def receive_instagram(update: Update, context: ContextTypes.DEFAULT_TYPE):
    link = update.message.text
    context.user_data["ig_url"] = None if link == "/skip" else link
    await update.message.reply_text("🔗 Endi **Telegram** kanal linkini yuboring (yoki /skip):")
    return WAITING_FOR_TELEGRAM

async def receive_telegram(update: Update, context: ContextTypes.DEFAULT_TYPE):
    link = update.message.text
    context.user_data["tg_url"] = None if link == "/skip" else link
    
    user_tier = context.user_data.get("user_tier", "free")
    
    if user_tier in ["pro", "agency"]:
        keyboard = [
            [InlineKeyboardButton("1️⃣ Oxirgi 10 ta post", callback_data="limit_10")],
            [InlineKeyboardButton("♾️ Hammasi (Max 50)", callback_data="limit_50")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("📊 **Nechta postni tahlil qilamiz?**", reply_markup=reply_markup)
        return WAITING_FOR_LIMIT

    await update.message.reply_text("⏳ **Ma'lumot yig'ilmoqda...**\nSkrining va AI tahlili biroz vaqt oladi (1-2 daqiqa).")
    
    try:
        # Default limits for Free
        audit = await audit_engine.perform_audit(
            context.user_data["audit_id"],
            context.user_data["ig_url"],
            context.user_data["tg_url"],
            ig_limit=12,
            tg_limit=20
        )
        
        return await process_audit_result(update, context, audit)

    except Exception as e:
        logger.error(f"Handler error: {e}")
        await update.message.reply_text("❌ Tizim xatosi. Keyinroq urinib ko'ring.")

    return ConversationHandler.END

async def receive_limit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    limit_map = {"limit_10": 10, "limit_50": 50}
    limit = limit_map.get(query.data, 10)
    
    await query.edit_message_text(f"⏳ **Ma'lumot yig'ilmoqda...** ({limit} post tahlil qilinmoqda)\nBiroz kuting...")
    
    try:
        audit = await audit_engine.perform_audit(
            context.user_data["audit_id"],
            context.user_data["ig_url"],
            context.user_data["tg_url"],
            ig_limit=limit,
            tg_limit=limit if limit == 10 else 100 
        )
        return await process_audit_result(update, context, audit)
    except Exception as e:
        logger.error(f"Limit Handler error: {e}")
        await query.message.reply_text("❌ Xatolik yuz berdi.")
        return ConversationHandler.END

async def process_audit_result(update: Update, context: ContextTypes.DEFAULT_TYPE, audit):
    # Handle message source (CallbackQuery or Message)
    message = update.message if update.message else update.callback_query.message

    if audit and audit.status == "completed":
        rep = audit.report_json
        context.user_data["last_report"] = rep
        
        # 1. Text Report
        messages = Formatter.format_report_to_messages(rep)
        for msg in messages:
            await message.reply_text(msg, parse_mode="Markdown")
        
        # 2. Charts
        charts = {}
        try:
            import re
            eng_str = rep.get("quick_audit", ["0% щ"])[0] 
            nums = re.findall(r"[-+]?\d*\.\d+|\d+", str(eng_str))
            eng_val = float(nums[0]) if nums else 2.5
            
            gauge_buf = ChartService.create_engagement_gauge(eng_val)
            if gauge_buf:
                charts["engagement"] = gauge_buf
                await message.reply_photo(photo=gauge_buf, caption="📊 Engagement Rate")
                gauge_buf.seek(0)
        except Exception as e:
            logger.error(f"Gauge Error: {e}")

        dist_buf = ChartService.create_post_distribution(5, 7)
        if dist_buf:
            charts["distribution"] = dist_buf
            dist_buf.seek(0)

        # 3. PDF
        user_tier = context.user_data.get("user_tier", "free")
        if user_tier in ["pro", "agency"]:
            pdf_bytes = ReportGenerator.generate_pdf(rep, charts, tier=user_tier)
            if pdf_bytes:
                await message.reply_document(
                    document=io.BytesIO(pdf_bytes),
                    filename=f"SMMind_Audit.pdf",
                    caption="📄 **Batafsil PDF Hisoboti**",
                    parse_mode="Markdown"
                )
        else:
                await message.reply_text("🔒 **PDF Hisobot** faqat PRO foydalanuvchilar uchun. /pricing")

        # 4. CTA and Navigation
        keyboard = [
            [InlineKeyboardButton("✍️ Post Yozish (AI)", callback_data="gen_post")],
            [InlineKeyboardButton("🚀 Yangi Audit", callback_data="start_audit_again")],
            [InlineKeyboardButton("🏠 Bosh Sahifa", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await message.reply_text("✅ Tahlil yakunlandi! Davom etamizmi?", reply_markup=reply_markup)

    else:
        err = audit.error_message if audit else "Unknown error"
        await message.reply_text(f"❌ Xatolik yuz berdi: {err}\nQayta urinib ko'ring: /audit")

    return ConversationHandler.END

async def pricing_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    db_user = await user_service.get_user(user_id)
    current_tier = db_user.tier if db_user else "free"
    
    txt = (
        f"💎 **Obuna holati**: {current_tier.upper()}\n\n"
        "📊 **Tariflar:**\n"
        "1️⃣ **FREE (Bepul)**: Kuniga 1 audit, PDF yo'q.\n"
        "2️⃣ **PRO ($3.9/oy)**: Cheksiz audit, PDF, AI Post.\n"
        "3️⃣ **AGENCY ($19/oy)**: White-label PDF, Menejer + Calendar.\n\n"
        "💡 **PRO sotib olish uchun:**\n"
        "To'lov qilish va akkauntni kuchaytirish uchun **@fibotai** ga murojaat qiling.\n"
        "Admin sizni to'lovdan so'ng darhol aktivlashtiradi."
    )
    
    keyboard = [
        [InlineKeyboardButton("💎 PRO sotib olish", url="https://t.me/fibotai")],
        [InlineKeyboardButton("🏢 AGENCY sotib olish", url="https://t.me/fibotai")],
        [InlineKeyboardButton("⬅️ Ortga", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.message.edit_text(txt, reply_markup=reply_markup, parse_mode="Markdown")
    else:
        await update.message.reply_text(txt, reply_markup=reply_markup, parse_mode="Markdown")

async def generate_post_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("💡 Post g'oyasi yozilmoqda...")
    
    user_tier = context.user_data.get("user_tier", "free")
    if user_tier == "free":
        await query.message.reply_text("🔒 Bu funksiya faqat PRO va AGENCY uchun!\n/pricing ni ko'ring.")
        return

    report = context.user_data.get("last_report")
    if not report:
        await query.edit_message_text("❌ Avval audit qilishingiz kerak.")
        return

    try:
        idea = await gemini_service.generate_post_idea(report)
        caption = idea.get("caption", "")
        img_prompt = idea.get("image_prompt", "")
        
        txt = (
            f"📝 **Mavzu:** {idea.get('topic')}\n"
            f"📌 **Format:** {idea.get('format')}\n\n"
            f"{caption}\n\n"
            f"🎨 **Rasm Prompti:**\n`{img_prompt}`"
        )
        keyboard = [[InlineKeyboardButton("⬅️ Ortga", callback_data="main_menu")]]
        await query.message.reply_text(txt, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Callback Error: {e}")
        await query.message.reply_text("❌ Xatolik.")

async def cancel(update: Update, context):
    await update.message.reply_text("Bekor qilindi.", reply_markup=await get_main_menu_keyboard())
    return ConversationHandler.END
