import os
import threading
from flask import Flask
from bot import run_bot

app = Flask(__name__)

@app.route('/')
@app.route('/health')
def health():
    return "✅ Бот погоды работает", 200

if __name__ == '__main__':
    # Запускаем бота в фоновом потоке
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    # Запускаем Flask
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# Для Gunicorn (на Render)
# При импорте модуля тоже запускаем бота
bot_thread = threading.Thread(target=run_bot)
bot_thread.daemon = True
bot_thread.start()