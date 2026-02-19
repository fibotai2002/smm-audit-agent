from telegram import Update, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler
from app.bot.states import WAITING_FOR_INSTAGRAM, WAITING_FOR_TELEGRAM
from app.services.audit_engine import AuditEngine
from app.services.user_service import UserService
from app.services.chart_service import ChartService
from app.services.pdf_service import ReportGenerator
from app.services.formatter import Formatter
from app.services.gemini_service import GeminiService
from app.db import AsyncSessionLocal
from app.models import Audit
from loguru import logger
import io

audit_engine = AuditEngine()
user_service = UserService()
gemini_service = GeminiService() # Initialize service

# Import Subscription Handlers
from app.bot.subscription_handlers import pricing_command, buy_subscription_callback
from sqlalchemy import select, func, and_
from datetime import datetime, timedelta
from app.models import User

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await user_service.get_or_create_user(user.id, user.username, user.full_name)
    
    txt = (
        f"👋 **Salom, {user.full_name}!**\n\n"
        "Men **SMMind AI**man.\n"
        "Instagram va Telegram profillarni tahlil qilish uchun /audit ni bosing."
    )
    await update.message.reply_text(txt, parse_mode="Markdown")

async def start_audit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await user_service.get_or_create_user(user_id, update.effective_user.username, update.effective_user.full_name)

    async with AsyncSessionLocal() as db:
        # Check User Tier
        user = await db.get(User, user_id)
        tier = user.tier if user else "free"
        
        # Check Limits for Free User
        if tier == "free":
            today = datetime.utcnow().date()
            stmt = select(func.count(Audit.id)).where(
                and_(
                    Audit.user_id == user_id,
                    func.date(Audit.created_at) == today
                )
            )
            result = await db.execute(stmt)
            count = result.scalar()
            
            if count >= 1:
                await update.message.reply_text(
                    "❌ **Kunlik limit tugadi!**\n\n"
                    "Bepul tarifda kuniga faqat 1 ta audit qilish mumkin.\n"
                    "Cheklovni olib tashlash uchun PRO ga o'ting: /pricing"
                )
                return ConversationHandler.END

        audit = Audit(user_id=user_id)
        db.add(audit)
        await db.commit()
        await db.refresh(audit)
        context.user_data["audit_id"] = audit.id
        context.user_data["user_tier"] = tier # Store tier for later use
    
    await update.message.reply_text("🔗 **Instagram** profilingiz linkini yuboring (yoki /skip):")
    return WAITING_FOR_INSTAGRAM

async def receive_instagram(update: Update, context: ContextTypes.DEFAULT_TYPE):
    link = update.message.text
    context.user_data["ig_url"] = None if link == "/skip" else link
    await update.message.reply_text("🔗Endi **Telegram** kanal linkini yuboring (yoki /skip):")
    return WAITING_FOR_TELEGRAM

async def receive_telegram(update: Update, context: ContextTypes.DEFAULT_TYPE):
    link = update.message.text
    context.user_data["tg_url"] = None if link == "/skip" else link
    
    await update.message.reply_text("⏳ **Ma'lumot yig'ilmoqda...**\nSkrining va AI tahlili biroz vaqt oladi (1-2 daqiqa).")
    
    try:
        audit = await audit_engine.perform_audit(
            context.user_data["audit_id"],
            context.user_data["ig_url"],
            context.user_data["tg_url"]
        )
        
        if audit and audit.status == "completed":
            rep = audit.report_json
            context.user_data["last_report"] = rep # Save for content generation
            
            # --- 1. Send Text Report ---
            messages = Formatter.format_report_to_messages(rep)
            for msg in messages:
                await update.message.reply_text(msg, parse_mode="Markdown")
            
            # --- 2. Send Charts ---
            charts = {}
            try:
                import re
                eng_str = rep.get("quick_audit", ["0% щ"])[0] 
                nums = re.findall(r"[-+]?\d*\.\d+|\d+", str(eng_str))
                eng_val = float(nums[0]) if nums else 2.5
                
                gauge_buf = ChartService.create_engagement_gauge(eng_val)
                if gauge_buf:
                    charts["engagement"] = gauge_buf
                    await update.message.reply_photo(photo=gauge_buf, caption="📊 Engagement Rate")
                    gauge_buf.seek(0)
            except Exception as e:
                logger.error(f"Gauge Error: {e}")

            dist_buf = ChartService.create_post_distribution(5, 7)
            if dist_buf:
                charts["distribution"] = dist_buf
                dist_buf.seek(0)

            # --- 3. Send PDF ---
            # Check if user allowed to get PDF (Pro/Agency)
            user_tier = context.user_data.get("user_tier", "free")
            
            if user_tier in ["pro", "agency"]:
                pdf_bytes = ReportGenerator.generate_pdf(rep, charts, tier=user_tier)
                if pdf_bytes:
                    await update.message.reply_document(
                        document=io.BytesIO(pdf_bytes),
                        filename=f"SMMind_Audit_{context.user_data.get('audit_id')}.pdf",
                        caption="📄 **Batafsil PDF Hisoboti**",
                        parse_mode="Markdown"
                    )
            else:
                 await update.message.reply_text("🔒 **PDF Hisobot** faqat PRO foydalanuvchilar uchun. /pricing")
                    parse_mode="Markdown"
                )

            # --- 4. Call to Action Button ---
            keyboard = [
                [InlineKeyboardButton("✍️ Post Yozish (AI)", callback_data="gen_post")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                "✅ Tahlil yakunlandi! Endi nima qilamiz?", 
                reply_markup=reply_markup
            )

        else:
            err = audit.error_message if audit else "Unknown error"
            await update.message.reply_text(f"❌ Xatolik yuz berdi: {err}\nQayta urinib ko'ring: /audit")
            
    except Exception as e:
        logger.error(f"Handler error: {e}")
        await update.message.reply_text("❌ Tizim xatosi. Keyinroq urinib ko'ring.")

    return ConversationHandler.END

async def generate_post_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("💡 Post g'oyasi yozilmoqda...")
    
    report = context.user_data.get("last_report")
    if not report:
        await query.edit_message_text("❌ Avval audit qilishingiz kerak.")
        return

    # Check Tier for Post Gen
    user_tier = context.user_data.get("user_tier", "free")
    if user_tier == "free":
        await query.answer("🔒 Bu funksiya faqat PRO uchun!", show_alert=True)
        return

    try:
        idea = await gemini_service.generate_post_idea(report)
        
        caption = idea.get("caption", "")
        hashtags = " ".join(idea.get("hashtags", []))
        img_prompt = idea.get("image_prompt", "")
        
        txt = (
            f"📝 **Mavzu:** {idea.get('topic')}\n"
            f"📌 **Format:** {idea.get('format')}\n\n"
            f"{caption}\n\n"
            f"{hashtags}\n\n"
            f"🎨 **Rasm Prompti (Midjourney):**\n`{img_prompt}`"
        )
        
        await query.message.reply_text(txt, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Callback Error: {e}")
        await query.message.reply_text("❌ Xatolik yuz berdi.")

async def cancel(update: Update, context):
    await update.message.reply_text("Bekor qilindi.")
    return ConversationHandler.END
