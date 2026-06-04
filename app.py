import os
import threading
from flask import Flask
from bot import run_bot

app = Flask(__name__)

@app.route('/')
@app.route('/health')
def health():
    return "✅ Бот погоды работает", 200

def run_flask():
    """Запускает Flask в фоновом потоке"""
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

if __name__ == '__main__':
    # Запускаем Flask в фоновом потоке
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    # Запускаем бота в ГЛАВНОМ потоке
    run_bot()