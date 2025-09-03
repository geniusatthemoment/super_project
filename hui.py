import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

# Замените 'YOUR_BOT_TOKEN' на реальный токен бота
TOKEN = '8474625217:AAF9TRFtnkCRikD_9wTUl_zBbV4O6gOcZ84'
bot = telebot.TeleBot(TOKEN)

# Список ID админов (замени на свой ID после получения)
ADMIN_IDS = [563057258]  # Вставь сюда свой Telegram ID

# Проверка, является ли пользователь админом
def is_admin(user_id):
    return user_id in ADMIN_IDS

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton('/info'))
    bot.send_message(message.chat.id, 'Привет! Это бот с разным доступом. Попробуй /info.', reply_markup=markup)

# Обработчик команды /info с разным выводом
@bot.message_handler(commands=['info'])
def info(message):
    user_id = message.from_user.id
    if is_admin(user_id):
        bot.send_message(message.chat.id, 'Привет, админ! Ты видишь секретную информацию: доступ ко всем настройкам бота.')
    else:
        bot.send_message(message.chat.id, 'Привет, пользователь! У тебя обычный доступ, только базовая информация.')

# Запуск бота
if __name__ == '__main__':
    bot.polling(none_stop=True)