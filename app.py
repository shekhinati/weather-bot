import os
import threading
from flask import Flask
from bot import run_bot

app = Flask(__name__)

@app.route('/')
@app.route('/health')
def health():
    return "✅ Бот погоды работает", 200

# Запускаем бота в фоновом потоке при старте приложения
bot_thread = threading.Thread(target=run_bot)
bot_thread.daemon = True
bot_thread.start()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)