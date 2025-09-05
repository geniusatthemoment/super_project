from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

def user_menu() -> ReplyKeyboardMarkup:
    b = ReplyKeyboardBuilder()
    b.add(KeyboardButton(text="Навигатор помощи"))
    b.add(KeyboardButton(text="Куда обращаться?"))
    b.add(KeyboardButton(text="Тревожная кнопка"))
    b.add(KeyboardButton(text="Анонсы мероприятий"))
    b.add(KeyboardButton(text="Задать вопрос"))
    return b.as_markup(resize_keyboard=True)

def admin_mode_menu() -> ReplyKeyboardMarkup:
    b = ReplyKeyboardBuilder()
    b.add(KeyboardButton(text="Режим пользователя"))
    b.add(KeyboardButton(text="Админ-панель"))
    return b.as_markup(resize_keyboard=True)

def admin_panel() -> ReplyKeyboardMarkup:
    b = ReplyKeyboardBuilder()
    b.add(KeyboardButton(text="Добавить мероприятие"))
    b.add(KeyboardButton(text="Просмотреть вопросы"))
    b.add(KeyboardButton(text="Добавить админа"))
    b.add(KeyboardButton(text="Вернуться к выбору режима"))
    return b.as_markup(resize_keyboard=True)

def help_navigator() -> ReplyKeyboardMarkup:
    b = ReplyKeyboardBuilder()
    b.add(KeyboardButton(text="Мне нужна помощь"))
    b.add(KeyboardButton(text="Хочу сообщить о проблеме"))
    b.add(KeyboardButton(text="Вернуться в главное меню"))
    return b.as_markup(resize_keyboard=True)
