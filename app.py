import os
import threading
import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from flask import Flask

# ===== ВСТАВЬ СВОИ ДАННЫЕ =====
TOKEN = '8843918701:AAGUxTkjFTTu2YG_-VO2k7Fbo98S8JYTZwU'
WEATHER_API_KEY = '223e7a7c7f4e761f1243d8faddb8f676'
# ===============================

# Создаём Flask-приложение для веб-сервера
app = Flask(__name__)

@app.route('/')
def home():
    return "Бот работает!", 200

@app.route('/health')
def health():
    return "OK", 200

# Функция погоды (та же самая)
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

# Обработчик сообщений Telegram
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city = update.message.text.strip()
    await update.message.reply_text(f"🔍 Смотрю погоду в {city}...")
    
    weather_info = get_weather(city)
    await update.message.reply_text(weather_info)

# Функция для запуска Telegram-бота в отдельном потоке
def run_telegram_bot():
    telegram_app = Application.builder().token(TOKEN).build()
    telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🤖 Telegram-бот запущен")
    telegram_app.run_polling()

# Запуск всего вместе
if __name__ == '__main__':
    # Запускаем Telegram-бота в фоновом потоке
    bot_thread = threading.Thread(target=run_telegram_bot)
    bot_thread.start()
    
    # Запускаем Flask-сервер для Render (слушаем порт)
    port = int(os.environ.get("PORT", 5000))
    print(f"🌐 Веб-сервер запущен на порту {port}")
    app.run(host="0.0.0.0", port=port)