import os
import time
import threading
import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from flask import Flask

# ===== ТОКЕН И КЛЮЧ ИЗ ПЕРЕМЕННЫХ ОКРУЖЕНИЯ =====
TOKEN = os.environ.get('TOKEN')
WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY')
# =================================================

if not TOKEN:
    print("❌ Ошибка: переменная TOKEN не задана!")
if not WEATHER_API_KEY:
    print("❌ Ошибка: переменная WEATHER_API_KEY не задана!")

app = Flask(__name__)

@app.route('/')
def home():
    return "Бот работает!", 200

@app.route('/health')
def health():
    return "OK", 200

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
            return f"❌ Город '{city_name}' не найден. Проверь название."
    except Exception as e:
        return f"⚠️ Ошибка: {e}"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city = update.message.text.strip()
    await update.message.reply_text(f"🔍 Смотрю погоду в {city}...")
    
    weather_info = get_weather(city)
    await update.message.reply_text(weather_info)

def run_telegram_bot():
    """Запускает Telegram-бота в отдельном потоке"""
    print("🤖 Запуск Telegram-бота...")
    telegram_app = Application.builder().token(TOKEN).build()
    telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ Telegram-бот успешно запущен и слушает сообщения")
    telegram_app.run_polling()

if __name__ == '__main__':
    # Запускаем Telegram-бота в фоновом потоке
    bot_thread = threading.Thread(target=run_telegram_bot)
    bot_thread.daemon = True  # Поток завершится вместе с основным процессом
    bot_thread.start()
    
    # Даём потоку время на инициализацию (важно для Render)
    time.sleep(2)
    
    # Запускаем Flask-сервер для Render
    port = int(os.environ.get("PORT", 5000))
    print(f"🌐 Веб-сервер запущен на порту {port}")
    app.run(host="0.0.0.0", port=port)