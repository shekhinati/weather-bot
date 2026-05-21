import os
import asyncio
import requests
from flask import Flask
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

TOKEN = os.environ.get('TOKEN')
WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY')

app = Flask(__name__)

@app.route('/')
def home():
    return "Бот работает!", 200

def get_weather(city_name: str) -> str:
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={WEATHER_API_KEY}&units=metric&lang=ru'
    try:
        response = requests.get(url)
        data = response.json()
        if data.get('cod') == 200:
            temp = data['main']['temp']
            feels = data['main']['feels_like']
            desc = data['weather'][0]['description']
            city = data['name']
            country = data['sys']['country']
            return f"🌍 {city}, {country}\n🌡 {temp}°C (ощущается как {feels}°C)\n📝 {desc.capitalize()}"
        else:
            return f"❌ Город '{city_name}' не найден."
    except Exception as e:
        return f"⚠️ Ошибка: {e}"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city = update.message.text.strip()
    await update.message.reply_text(f"🔍 Смотрю погоду в {city}...")
    weather_info = get_weather(city)
    await update.message.reply_text(weather_info)

# Запускаем бота (НЕ в отдельном потоке)
def start_bot():
    print("🤖 Запуск Telegram-бота...")
    telegram_app = Application.builder().token(TOKEN).build()
    telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ Telegram-бот успешно запущен")
    telegram_app.run_polling()

if __name__ == "__main__":
    start_bot()
else:
    # Этот код выполняется, когда Gunicorn импортирует app.py
    # Запускаем бота в фоне с помощью asyncio (без потоков)
    import threading
    bot_thread = threading.Thread(target=start_bot)
    bot_thread.daemon = True
    bot_thread.start()