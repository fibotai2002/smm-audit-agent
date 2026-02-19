from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from telegram import Update
from smm_audit.settings import TELEGRAM_BOT_TOKEN
from bot.management.commands.runbot import Command
import json
import asyncio
from asgiref.sync import async_to_sync

# Initialize the bot app globally to reuse it
bot_command = Command()
application = bot_command.get_application()

@csrf_exempt
def telegram_webhook(request):
    if request.method == "POST":
        try:
            update = Update.de_json(json.loads(request.body.decode('utf-8')), application.bot)
            async_to_sync(application.process_update)(update)
            return JsonResponse({"status": "ok"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    return JsonResponse({"status": "error"}, status=400)
