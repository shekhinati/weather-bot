import os
import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# Токены из переменных окружения
TOKEN = os.getenv('TELEGRAM_TOKEN')
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')

# Проверка при запуске
if not TOKEN or not WEATHER_API_KEY:
    raise ValueError("❌ Задайте переменные TELEGRAM_TOKEN и WEATHER_API_KEY")

def get_weather(city_name: str) -> str:
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
            return f"❌ Город '{city_name}' не найден. Проверь название."
    except Exception as e:
        return f"⚠️ Ошибка: {e}"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city = update.message.text.strip()
    await update.message.reply_text(f"🔍 Смотрю погоду в {city}...")
    weather_info = get_weather(city)
    await update.message.reply_text(weather_info)

def run_bot():
    """Запуск бота (будет вызван из app.py)"""
    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print('☁️ Бот погоды запущен и слушает сообщения')
    app.run_polling()

if __name__ == '__main__':
    run_bot()