import os
import time
import threading
import requests
from flask import Flask
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

TOKEN = os.environ.get('TOKEN')
WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY')

print(f"=== ДИАГНОСТИКА ===")
print(f"TOKEN: {'✅' if TOKEN else '❌'} (начинается с {TOKEN[:10] if TOKEN else 'НЕТ'}...)")
print(f"WEATHER_API_KEY: {'✅' if WEATHER_API_KEY else '❌'}")

app = Flask(__name__)

@app.route('/')
def home():
    return "Бот работает!", 200

def get_weather(city_name: str) -> str:
    if not WEATHER_API_KEY:
        return "❌ Ошибка: API ключ погоды не задан"
    
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={WEATHER_API_KEY}&units=metric&lang=ru'
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        if data.get('cod') == 200:
            temp = data['main']['temp']
            feels = data['main']['feels_like']
            desc = data['weather'][0]['description']
            city = data['name']
            country = data['sys']['country']
            return f"🌍 {city}, {country}\n🌡 {temp}°C (ощущается как {feels}°C)\n📝 {desc.capitalize()}"
        else:
            return f"❌ Город '{city_name}' не найден. Код: {data.get('cod')}"
    except Exception as e:
        return f"⚠️ Ошибка: {e}"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city = update.message.text.strip()
    print(f"📩 Получено сообщение: {city}")
    await update.message.reply_text(f"🔍 Смотрю погоду в {city}...")
    weather_info = get_weather(city)
    await update.message.reply_text(weather_info)
    print(f"✅ Ответ отправлен для {city}")

def run_flask():
    """Запускает Flask-сервер в фоновом потоке"""
    port = int(os.environ.get("PORT", 5000))
    print(f"🌐 Запуск Flask на порту {port}")
    app.run(host="0.0.0.0", port=port)

def run_telegram_bot():
    """Запускает Telegram-бота в главном потоке"""
    print("🤖 Запуск Telegram-бота...")
    telegram_app = Application.builder().token(TOKEN).build()
    telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ Telegram-бот успешно запущен и слушает сообщения")
    telegram_app.run_polling()

if __name__ == "__main__":
    # Запускаем Flask в фоновом потоке
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    # Даём Flask время на запуск
    time.sleep(2)
    
    # Запускаем Telegram-бота в главном потоке
    run_telegram_bot()
else:
    # Этот код выполняется, когда Gunicorn импортирует app.py
    # Запускаем бота в главном потоке (так нужно для Python 3.14)
    run_telegram_bot()