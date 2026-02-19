from django.core.management.base import BaseCommand
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackQueryHandler
from django.conf import settings
from bot.handlers import (
    start, start_audit_command, start_audit_callback, 
    receive_instagram, receive_telegram, cancel, 
    generate_post_callback, pricing_command, receive_limit,
    my_profile, help_command, main_menu_callback, tutorial_callback
)
from bot.states import WAITING_FOR_INSTAGRAM, WAITING_FOR_TELEGRAM, WAITING_FOR_LIMIT
import logging

class Command(BaseCommand):
    help = 'Runs the Telegram Bot'

    def handle(self, *args, **options):
        # Configure logging
        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=logging.INFO
        )

    def get_application(self):
        """Returns the application instance, building it if necessary."""
        return ApplicationBuilder().token(settings.TELEGRAM_BOT_TOKEN).build()

    def handle(self, *args, **options):
        # Configure logging
        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=logging.INFO
        )

        application = self.get_application()
        
        conv_handler = ConversationHandler(
            entry_points=[
                CommandHandler('audit', start_audit_command),
                CallbackQueryHandler(start_audit_callback, pattern="^start_audit$"),
                CallbackQueryHandler(start_audit_callback, pattern="^start_audit_again$")
            ],
            states={
                WAITING_FOR_INSTAGRAM: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_instagram), CommandHandler("skip", receive_instagram)],
                WAITING_FOR_TELEGRAM: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_telegram), CommandHandler("skip", receive_telegram)],
                WAITING_FOR_LIMIT: [CallbackQueryHandler(receive_limit, pattern="^limit_")],
            },
            fallbacks=[CommandHandler('cancel', cancel)]
        )
        
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("pricing", pricing_command))
        application.add_handler(CommandHandler("help", help_command))
        
        # Dashboard Callbacks
        application.add_handler(CallbackQueryHandler(my_profile, pattern="^my_profile$"))
        application.add_handler(CallbackQueryHandler(pricing_command, pattern="^pricing$"))
        application.add_handler(CallbackQueryHandler(help_command, pattern="^help$"))
        application.add_handler(CallbackQueryHandler(tutorial_callback, pattern="^tutorial$"))
        application.add_handler(CallbackQueryHandler(main_menu_callback, pattern="^main_menu$"))
        
        application.add_handler(conv_handler)
        application.add_handler(CallbackQueryHandler(generate_post_callback, pattern="gen_post"))

        self.stdout.write(self.style.SUCCESS('Bot started polling...'))
        application.run_polling()
