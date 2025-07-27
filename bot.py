import os
import json
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.error import TelegramError, NetworkError
import hmac
import hashlib

# Настройка логгирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Конфигурация
BOT_TOKEN = os.getenv('BOT_TOKEN') or '8432761852:AAF63_P30GSJJ5T3jLy8bIPZ0iAoTQrfIfo'
MINIAPP_URL = os.getenv('MINIAPP_URL') or 'C:/Users/yunxi/Desktop/mybot/mini_app/templates/index.html'
ITEMS_FILE = 'items.json'
REQUEST_TIMEOUT = 30  # Увеличиваем таймаут запросов

# Загрузка предметов из JSON файла
def load_items():
    try:
        with open(ITEMS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Error loading items: {e}")
        # Пример предметов по умолчанию
        default_items = [
            {"id": 1, "name": "Золотой аватар", "price": 50, "description": "Эксклюзивный золотой аватар"},
            {"id": 2, "name": "VIP статус", "price": 100, "description": "Доступ к VIP функциям"},
            {"id": 3, "name": "Бустер опыта", "price": 30, "description": "+20% опыта на 7 дней"}
        ]
        try:
            with open(ITEMS_FILE, 'w', encoding='utf-8') as f:
                json.dump(default_items, f, ensure_ascii=False, indent=2)
            return default_items
        except Exception as e:
            logger.error(f"Error creating default items: {e}")
            return []

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        keyboard = [
            [InlineKeyboardButton("Открыть магазин", web_app=WebAppInfo(url=MINIAPP_URL))]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Добро пожаловать в магазин! Нажмите кнопку ниже, чтобы открыть магазин.",
            reply_markup=reply_markup
        )
    except Exception as e:
        logger.error(f"Error in start command: {e}")
        await update.message.reply_text("Произошла ошибка. Пожалуйста, попробуйте позже.")

# Обработчик покупки
async def purchase(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    try:
        await query.answer()
        
        data = json.loads(query.data)
        item_id = data.get('item_id')
        items = load_items()
        item = next((i for i in items if i['id'] == item_id), None)
        
        if not item:
            await query.edit_message_text("Товар не найден.")
            return
        
        # Имитация покупки
        await query.edit_message_text(
            f"Вы успешно приобрели {item['name']} за {item['price']} звёзд!\n\n"
            "В реальном приложении здесь будет открытие платежного интерфейса Wallet."
        )
    except json.JSONDecodeError:
        await query.edit_message_text("Ошибка обработки запроса.")
    except Exception as e:
        logger.error(f"Error in purchase handler: {e}")
        await query.edit_message_text("Произошла ошибка при обработке покупки.")

async def post_init(application: Application):
    """Функция, вызываемая после инициализации бота"""
    try:
        me = await application.bot.get_me()
        logger.info(f"Бот @{me.username} успешно запущен!")
    except NetworkError as e:
        logger.error(f"Network error during initialization: {e}")
    except TelegramError as e:
        logger.error(f"Telegram error during initialization: {e}")
    except Exception as e:
        logger.error(f"Unexpected error during initialization: {e}")

def main():
    try:
        # Создаем Application с увеличенным таймаутом
        application = Application.builder() \
            .token(BOT_TOKEN) \
            .read_timeout(REQUEST_TIMEOUT) \
            .write_timeout(REQUEST_TIMEOUT) \
            .connect_timeout(REQUEST_TIMEOUT) \
            .pool_timeout(REQUEST_TIMEOUT) \
            .post_init(post_init) \
            .build()
        
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CallbackQueryHandler(purchase, pattern=r'^\{.*\}$'))
        
        logger.info("Запуск бота...")
        application.run_polling(
            poll_interval=1.0,
            timeout=REQUEST_TIMEOUT,
            drop_pending_updates=True
        )
    except Exception as e:
        logger.error(f"Fatal error in main: {e}")

if __name__ == "__main__":
    main()