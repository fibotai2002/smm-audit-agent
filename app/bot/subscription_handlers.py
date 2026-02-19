from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import ContextTypes
from app.db import AsyncSessionLocal
from app.models import User
from datetime import datetime, timedelta
from loguru import logger
from sqlalchemy import select

async def pricing_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Shows subscription tiers and allows users to upgrade.
    """
    user = update.effective_user
    user_id = user.id
    
    expires_at = None
    current_tier = "free"

    # Check current status
    async with AsyncSessionLocal() as db:
        stmt = select(User).where(User.telegram_id == user_id)
        result = await db.execute(stmt)
        db_user = result.scalar_one_or_none()
        
        if db_user:
            current_tier = db_user.tier
            expires_at = db_user.subscription_expires_at

    # Pricing Text
    txt = f"💎 **Sizning Obunangiz**: {current_tier.upper()}\n"
    
    if expires_at:
        txt += f"📅 Tugash vaqti: {expires_at.strftime('%Y-%m-%d %H:%M')}\n\n"
    else:
        txt += "\n"

    txt += (
        "📊 **Tariflar:**\n\n"
        "1️⃣ **FREE (Bepul)**\n"
        "• Kuniga 1 ta audit\n"
        "• ❌ PDF hisobot yo'q\n"
        "• ❌ AI Post Generator yo'q\n\n"
        "2️⃣ **PRO ($10/oy)**\n"
        "• ✅ Cheksiz auditlar\n"
        "• ✅ PDF hisobotlar\n"
        "• ✅ AI Post Generator\n"
        "• ✅ Prioritet qo'llab-quvvatlash\n\n"
        "3️⃣ **AGENCY ($50/oy)**\n"
        "• ✅ Barcha PRO imkoniyatlari\n"
        "• ✅ White-label PDF (SMMind logotipisiz)\n"
        "• ✅ Shaxsiy menejer (Telegram orqali)\n"
        "• ✅ Kelajakda: Raqobatchilar tahlili"
    )

    keyboard = [
        [InlineKeyboardButton("💎 PRO ga o'tish ($10)", callback_data="buy_pro")],
        [InlineKeyboardButton("🏢 AGENCY ga o'tish ($50)", callback_data="buy_agency")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(txt, reply_markup=reply_markup, parse_mode="Markdown")


async def buy_subscription_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles button clicks for buying subscriptions (Mock Payment).
    """
    query = update.callback_query
    # await query.answer() # Answered later or immediately

    data = query.data
    user_id = query.from_user.id
    
    new_tier = "free"
    days = 30
    
    if data == "buy_pro":
        new_tier = "pro"
    elif data == "buy_agency":
        new_tier = "agency"
    else:
        await query.answer("Noma'lum buyruq.")
        return

    # Mock Payment Processing...
    # In real app, here we would send an invoice or payment link.
    
    async with AsyncSessionLocal() as db:
        stmt = select(User).where(User.telegram_id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if user:
            user.tier = new_tier
            user.subscription_expires_at = datetime.utcnow() + timedelta(days=days)
            await db.commit()
            
            success_txt = (
                f"🎉 **Tabriklaymiz!**\n\n"
                f"Siz muvaffaqiyatli **{new_tier.upper()}** obunasiga o'tdingiz!\n"
                f"Amal qilish muddati: 30 kun.\n\n"
                f"Barcha cheklovlar olib tashlandi. /audit ni bosing!"
            )
            
            await query.answer("To'lov qabul qilindi! ✅", show_alert=True)
            await query.edit_message_text(success_txt, parse_mode="Markdown")
        else:
            await query.answer("Xatolik: Foydalanuvchi topilmadi.", show_alert=True)
