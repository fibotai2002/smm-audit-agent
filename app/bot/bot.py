from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackQueryHandler
from app.config import settings
from app.bot.handlers import start, start_audit, receive_instagram, receive_telegram, cancel, generate_post_callback
from app.bot.subscription_handlers import pricing_command, buy_subscription_callback
from app.bot.states import WAITING_FOR_INSTAGRAM, WAITING_FOR_TELEGRAM

def create_bot(post_init=None):
    builder = ApplicationBuilder().token(settings.TELEGRAM_BOT_TOKEN)
    if post_init:
        builder.post_init(post_init)
    
    app = builder.build()
    
    conv = ConversationHandler(
        entry_points=[CommandHandler('audit', start_audit)],
        states={
            WAITING_FOR_INSTAGRAM: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_instagram), CommandHandler("skip", receive_instagram)],
            WAITING_FOR_TELEGRAM: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_telegram), CommandHandler("skip", receive_telegram)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("pricing", pricing_command))
    app.add_handler(conv)
    app.add_handler(CallbackQueryHandler(generate_post_callback, pattern="gen_post")) # New Handler
    app.add_handler(CallbackQueryHandler(buy_subscription_callback, pattern="^buy_")) # Sub Handlers
    
    return app
