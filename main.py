import telebot
import smtplib
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = os.getenv('SMTP_PORT')
EMAIL_LOGIN = os.getenv('EMAIL_LOGIN')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

user_data = {}

def is_valid_email(email):
    regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(regex, email)

def send_email(recipient_email, message):
    try:
        msg = MIMEMultipart()
        msg["From"] = EMAIL_LOGIN
        msg["To"] = recipient_email
        msg["Subject"] = "Уведомление от Telegram-бота"
        msg.attach(MIMEText(message, "plain"))

        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(EMAIL_LOGIN, EMAIL_PASSWORD)
            server.sendmail(EMAIL_LOGIN, recipient_email, msg.as_string())
        return True
    except Exception as e:
        print(f"Ошибка отправки письма: {e}")
        return False

@bot.message_handler(commands=["start"])
def start_handler(message):
    bot.reply_to(message, "Привет! Укажите ваш email для отправки уведомлений.")
    user_data[message.chat.id] = {"email": None, "message": None}

@bot.message_handler(func=lambda msg: user_data.get(msg.chat.id, {}).get("email") is None)
def email_handler(message):
    email = message.text.strip()
    if is_valid_email(email):
        user_data[message.chat.id]["email"] = email
        bot.reply_to(message, "Email подтвержден. Введите текст сообщения, которое нужно отправить.")
    else:
        bot.reply_to(message, "Некорректный email. Попробуйте снова.")

@bot.message_handler(func=lambda msg: user_data.get(msg.chat.id, {}).get("email") is not None and user_data.get(msg.chat.id, {}).get("message") is None)
def message_handler(message):
    user_data[message.chat.id]["message"] = message.text.strip()
    email = user_data[message.chat.id]["email"]
    text = user_data[message.chat.id]["message"]

    if send_email(email, text):
        bot.reply_to(message, "Сообщение успешно отправлено!")
    else:
        bot.reply_to(message, "Ошибка при отправке сообщения. Попробуйте позже.")

    user_data.pop(message.chat.id, None)

if __name__ == "__main__":
    print("Бот запущен...")
    bot.polling(none_stop=True)
