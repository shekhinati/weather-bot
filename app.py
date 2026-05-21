import os
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
        return "❌ Ошибка: API ключ погоды не задан на сервере"
    
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
            return f"❌ Город '{city_name}' не найден. Код ошибки: {data.get('cod')}"
    except Exception as e:
        return f"⚠️ Ошибка при запросе погоды: {e}"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text.strip()
    print(f"📩 Получено сообщение: {user_message}")
    
    # Сначала отвечаем, что обрабатываем
    await update.message.reply_text(f"🔍 Ищу погоду в {user_message}...")
    
    # Получаем погоду
    weather_info = get_weather(user_message)
    
    # Отправляем результат
    await update.message.reply_text(weather_info)
    print(f"✅ Отправлен ответ для {user_message}")

def start_bot():
    print("🤖 Запуск Telegram-бота...")
    try:
        telegram_app = Application.builder().token(TOKEN).build()
        telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        print("✅ Telegram-бот успешно запущен и слушает сообщения")
        telegram_app.run_polling()
    except Exception as e:
        print(f"❌ Ошибка при запуске бота: {e}")

# Запускаем бота в фоновом потоке
bot_thread = threading.Thread(target=start_bot)
bot_thread.daemon = True
bot_thread.start()

# Даём время на запуск
import time
time.sleep(2)
print("🌐 Веб-сервер готов")