# SMM Audit Agent 🤖

Instagram va Telegram profillarni tahlil qiluvchi va AI yordamida professional audit tayyorlab beruvchi aqlli agent.

## Xususiyatlari
- **Instagram Scraping:** Public profillar tahlili (Login shart emas).
- **Telegram Scraping:** Ochiq kanallar tahlili.
- **AI Tahlil:** Google Gemini 3 Pro yordamida chuqur marketing auditi.
- **Telegram Bot:** Qulay interfeys va hisobot taqdimoti.

## O'rnatish

### 1. Talablar
- Docker & Docker Compose
- Telegram Bot Token
- Google Gemini API Key

### 2. Sozlash
Repozitoriyni klonlang va `.env` faylini yarating:
```bash
cp .env.example .env
```
`.env` faylini ochib, kalitlarni kiriting:
```ini
TELEGRAM_BOT_TOKEN=sizning_tokeningiz
GEMINI_API_KEY=sizning_gemini_kalitingiz
```

### 3. Ishga tushirish
Docker yordamida oson ishga tushiring:
```bash
docker-compose up --build -d
```

Yoki lokal muhitda:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
python -m app.main
```

## Botdan foydalanish
1. Botga `/start` bosing.
2. `/audit` komandasini yuboring.
3. Instagram va Telegram linklarini ketma-ket yuboring.
4. AI tahlilini kuting va natijani oling!

## Texnologiyalar
- **Python 3.11**
- **Aiogram / python-telegram-bot**
- **Playwright** (Scraping)
- **FastAPI**
- **SQLite** (Async)
- **Google Gemini**

## Muallif
SMM Audit Agent Team (c) 2026
