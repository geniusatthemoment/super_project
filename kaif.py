import asyncio
import json
import os
import uuid
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from dotenv import load_dotenv
load_dotenv()
TOKEN = os.getenv("TOKEN")


ADMIN_IDS = [563057258]

# Путь к JSON-файлу
DATA_FILE = 'bot_data.json'

# Инициализация JSON-файла
def init_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w') as f:
            json.dump({'events': [], 'questions': [], 'admins': ADMIN_IDS}, f)
    else:
        data = read_data()
        data['admins'] = list(set(data.get('admins', []) + ADMIN_IDS))
        write_data(data)

# Чтение данных из JSON
def read_data():
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

# Запись данных в JSON
def write_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

init_data()

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Определение состояний для FSM
class UserStates(StatesGroup):
    HelpTopic = State()
    ReportProblem = State()
    AskQuestion = State()
    AddEvent = State()
    AddAdmin = State()

# Проверка админ-прав
def is_admin(user_id):
    data = read_data()
    return user_id in data['admins']

# Меню пользователя
def user_menu():
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="Навигатор помощи"))
    builder.add(KeyboardButton(text="Куда обращаться?"))
    builder.add(KeyboardButton(text="Тревожная кнопка"))
    builder.add(KeyboardButton(text="Анонсы мероприятий"))
    builder.add(KeyboardButton(text="Задать вопрос"))
    return builder.as_markup(resize_keyboard=True)

# Меню выбора режима для админа
def admin_mode_menu():
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="Режим пользователя"))
    builder.add(KeyboardButton(text="Админ-панель"))
    return builder.as_markup(resize_keyboard=True)

# Админ-панель
def admin_panel():
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="Добавить мероприятие"))
    builder.add(KeyboardButton(text="Просмотреть вопросы"))
    builder.add(KeyboardButton(text="Добавить админа"))
    builder.add(KeyboardButton(text="Вернуться к выбору режима"))
    return builder.as_markup(resize_keyboard=True)

# Навигатор помощи
def help_navigator():
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="Мне нужна помощь"))
    builder.add(KeyboardButton(text="Хочу сообщить о проблеме"))
    builder.add(KeyboardButton(text="Вернуться в главное меню"))
    return builder.as_markup(resize_keyboard=True)

# Обработчик команды /start
@dp.message(Command("start"))
async def start(message: types.Message):
    user_id = message.from_user.id
    if is_admin(user_id):
        await message.answer("Выберите режим работы:", reply_markup=admin_mode_menu())
    else:
        await message.answer("Добро пожаловать! Это бот психологической помощи.", reply_markup=user_menu())

# Обработчик текстовых сообщений
@dp.message()
async def handle_text(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    text = message.text

    if text == "Режим пользователя" and is_admin(user_id):
        await message.answer("Переключено на режим пользователя.", reply_markup=user_menu())

    elif text == "Админ-панель" and is_admin(user_id):
        await message.answer("Админ-панель:", reply_markup=admin_panel())

    elif text == "Вернуться к выбору режима" and is_admin(user_id):
        await message.answer("Выберите режим работы:", reply_markup=admin_mode_menu())

    elif text == "Навигатор помощи":
        await message.answer("Выберите опцию:", reply_markup=help_navigator())

    elif text == "Мне нужна помощь":
        await message.answer("Выберите тему:\n1. Стресс\n2. Депрессия\n3. Кибербуллинг")
        await state.set_state(UserStates.HelpTopic)

    elif text == "Хочу сообщить о проблеме":
        await message.answer("Опишите проблему кратко:")
        await state.set_state(UserStates.ReportProblem)

    elif text == "Куда обращаться?":
        contacts = (
            "📞 Психологическая помощь (Томск):\n"
            "- Горячая линия: 8-800-2000-122\n"
            "- Центр псих. помощи: +7 (3822) 123-456\n\n"
            "🚨 Правоохранительные органы:\n"
            "- Полиция Томской области: 102\n"
            "- УМВД Томск: +7 (3822) 789-000"
        )
        await message.answer(contacts, reply_markup=user_menu())

    elif text == "Тревожная кнопка":
        await message.answer(
            "🚨 Если вы в опасности:\n1. Позвоните 112\n2. Дышите медленно: вдох 4 сек, выдох 4 сек\n"
            "Свяжитесь с горячей линией: 8-800-2000-122",
            reply_markup=user_menu()
        )

    elif text == "Анонсы мероприятий":
        data = read_data()
        events = data['events']
        if events:
            response = "📅 Предстоящие мероприятия:\n"
            for event in events:
                response += f"- {event['title']} ({event['date']}): {event['description']}\n"
        else:
            response = "Мероприятий пока нет."
        await message.answer(response, reply_markup=user_menu())

    elif text == "Задать вопрос":
        await message.answer("Введите ваш вопрос для экспертов ЦМП:")
        await state.set_state(UserStates.AskQuestion)

    elif text == "Добавить мероприятие" and is_admin(user_id):
        await message.answer(
            "Введите данные мероприятий (формат: Название|Дата|Описание;Название2|Дата2|Описание2 или одно мероприятие: Название|Дата|Описание):"
        )
        await state.set_state(UserStates.AddEvent)

    elif text == "Просмотреть вопросы" and is_admin(user_id):
        data = read_data()
        questions = data['questions']
        if questions:
            response = "📋 Вопросы пользователей:\n"
            for q in questions:
                response += f"ID: {q['id']}, Пользователь: {q['user_id']}, Вопрос: {q['question']}, Статус: {q['status']}\n"
        else:
            response = "Вопросов нет."
        await message.answer(response, reply_markup=admin_panel())

    elif text == "Добавить админа" and is_admin(user_id):
        await message.answer("Введите Telegram ID администраторов (через запятую, например: 123456,789012):")
        await state.set_state(UserStates.AddAdmin)

    elif text == "Вернуться в главное меню":
        await message.answer("Главное меню:", reply_markup=user_menu())

# Обработчик тем помощи
@dp.message(UserStates.HelpTopic)
async def handle_help_topic(message: types.Message, state: FSMContext):
    topic = message.text
    if topic == "1":
        await message.answer(
            "Совет по стрессу: попробуйте дыхательные упражнения. Свяжитесь: 8-800-2000-122",
            reply_markup=user_menu()
        )
    elif topic == "2":
        await message.answer(
            "При депрессии важно говорить с близкими. Горячая линия: 8-800-2000-122",
            reply_markup=user_menu()
        )
    elif topic == "3":
        await message.answer(
            "При кибербуллинге сохраняйте доказательства. Контакты полиции: 102",
            reply_markup=user_menu()
        )
    else:
        await message.answer("Пожалуйста, выберите 1, 2 или 3.", reply_markup=user_menu())
    await state.clear()

# Обработчик сообщений о проблеме
@dp.message(UserStates.ReportProblem)
async def handle_report(message: types.Message, state: FSMContext):
    await message.answer(
        "Ваше сообщение принято. Обратитесь в полицию (102) или горячую линию (8-800-2000-122).",
        reply_markup=user_menu()
    )
    await state.clear()

# Обработчик вопросов
@dp.message(UserStates.AskQuestion)
async def handle_question(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    question = message.text
    data = read_data()
    data['questions'].append({
        'id': str(uuid.uuid4()),
        'user_id': user_id,
        'question': question,
        'status': 'Новое'
    })
    write_data(data)
    await message.answer("Ваш вопрос отправлен экспертам!", reply_markup=user_menu())
    await state.clear()

# Обработчик добавления мероприятий
@dp.message(UserStates.AddEvent)
async def handle_add_event(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if not is_admin(user_id):
        await state.clear()
        return
    data = read_data()
    events_input = message.text.strip().split(';')
    added_count = 0
    error_messages = []

    for event_str in events_input:
        try:
            title, date, description = event_str.split('|')
            data['events'].append({
                'id': str(uuid.uuid4()),
                'title': title.strip(),
                'date': date.strip(),
                'description': description.strip()
            })
            added_count += 1
        except ValueError:
            error_messages.append(f"Ошибка в формате: {event_str}. Используйте: Название|Дата|Описание")

    if added_count > 0:
        write_data(data)
        response = f"Успешно добавлено {added_count} мероприятие(й)!"
    else:
        response = "Ни одно мероприятие не добавлено."

    if error_messages:
        response += "\nОшибки:\n" + "\n".join(error_messages)

    await message.answer(response, reply_markup=admin_panel())
    await state.clear()

# Обработчик добавления админов
@dp.message(UserStates.AddAdmin)
async def handle_add_admin(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if not is_admin(user_id):
        await state.clear()
        return
    data = read_data()
    admin_ids_input = message.text.strip().split(',')
    added_count = 0
    error_messages = []
    existing_admins = []

    for admin_id in admin_ids_input:
        try:
            new_admin_id = int(admin_id.strip())
            if new_admin_id not in data['admins']:
                data['admins'].append(new_admin_id)
                added_count += 1
            else:
                existing_admins.append(str(new_admin_id))
        except ValueError:
            error_messages.append(f"Ошибка: {admin_id} не является числовым Telegram ID.")

    if added_count > 0:
        write_data(data)
        response = f"Успешно добавлено {added_count} администратор(ов)!"
    else:
        response = "Ни один администратор не добавлен."

    if existing_admins:
        response += f"\nСледующие ID уже в списке админов: {', '.join(existing_admins)}"
    if error_messages:
        response += "\nОшибки:\n" + "\n".join(error_messages)

    await message.answer(response, reply_markup=admin_panel())
    await state.clear()

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())