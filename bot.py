import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InputFile

# ТВОЙ ТОКЕН БОТА
TOKEN = "7596288699:AAGYjVVDkZi6DArWVcrwK9snbcSHs2MrvRE"

# ID АДМИНА (ТВОЙ TELEGRAM ID)
ADMIN_ID = 6813642998

# ПУТЬ К ФАЙЛУ КУРСА
COURSE_FILE_PATH = "Как зарабатывать в Instagram, TikTok без вложений"

# ПАПКА ДЛЯ СОХРАНЕНИЯ СКРИНШОТОВ ОПЛАТЫ
PAYMENTS_FOLDER = "payments"

# Создаём папку, если её нет
os.makedirs(PAYMENTS_FOLDER, exist_ok=True)

bot = telebot.TeleBot(TOKEN)

# Главное меню
@bot.message_handler(commands=["start"])
def send_welcome(message):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("Оплатить курс", callback_data="pay"))
    
    bot.send_message(
        message.chat.id,
        "🔥 Добро пожаловать!\n\n"
        "📘 Курс: Как заработать в Instagram/TikTok без вложений\n"
        "💰 Цена: 500 грн\n\n"
        "👉 Нажми на кнопку ниже, чтобы оплатить.",
        reply_markup=keyboard
    )

# Кнопка "Оплатить курс"
@bot.callback_query_handler(func=lambda call: call.data == "pay")
def send_payment_info(call):
    bot.send_message(
        call.message.chat.id,
        "💳 Отправь 500 грн на карту **1234 5678 9012 3456**\n"
        "После оплаты пришли сюда скриншот платежа."
    )

# Принимаем скриншот оплаты
@bot.message_handler(content_types=["photo"])
def handle_payment_confirmation(message):
    file_id = message.photo[-1].file_id
    file_info = bot.get_file(file_id)
    file_path = file_info.file_path

    # Сохраняем фото
    downloaded_file = bot.download_file(file_path)
    file_name = f"{PAYMENTS_FOLDER}/{message.chat.id}.jpg"
    with open(file_name, "wb") as file:
        file.write(downloaded_file)

    # Пересылаем админу
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("✅ Подтвердить оплату", callback_data=f"confirm_{message.chat.id}"))

    bot.send_photo(ADMIN_ID, open(file_name, "rb"), caption=f"💰 Новый платёж от {message.chat.id}", reply_markup=keyboard)
    bot.send_message(message.chat.id, "✅ Платёж отправлен на проверку. Ожидай подтверждения.")

# Подтверждение оплаты и отправка курса
@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_"))
def confirm_payment(call):
    user_id = int(call.data.split("_")[1])

    if os.path.exists(COURSE_FILE_PATH):
        bot.send_document(user_id, InputFile(COURSE_FILE_PATH), caption="🎉 Поздравляем! Вот твой курс.")
        bot.send_message(ADMIN_ID, f"✅ Оплата подтверждена! Курс отправлен {user_id}.")
    else:
        bot.send_message(user_id, "❌ Ошибка! Файл курса не найден.")
        bot.send_message(ADMIN_ID, "⚠️ Файл курса отсутствует!")

# Запуск бота
bot.polling()