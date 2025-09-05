from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
import uuid

from storage import read_data, write_data
from keyboards import user_menu, admin_mode_menu, admin_panel, help_navigator
from states import UserStates
from utils import is_admin

router = Router()

@router.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    """Handle the /start command, showing user or admin menu based on user role."""
    user_id = message.from_user.id
    if is_admin(user_id):
        await message.answer("Выберите режим работы:", reply_markup=admin_mode_menu())
    else:
        await message.answer("Добро пожаловать! Это бот психологической помощи.", reply_markup=user_menu())

@router.message()
async def handle_text(message: types.Message, state: FSMContext):
    """Handle text messages, routing to appropriate actions based on user input."""
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
        events = data.get('events', [])
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
        questions = data.get('questions', [])
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
    elif text == "Помощь от AI":
        await message.answer("", reply_markup=user_menu())

@router.message(UserStates.HelpTopic)
async def handle_help_topic(message: types.Message, state: FSMContext):
    """Handle user selection of help topics (stress, depression, cyberbullying)."""
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

@router.message(UserStates.ReportProblem)
async def handle_report(message: types.Message, state: FSMContext):
    """Handle user-submitted problem reports."""
    await message.answer(
        "Ваше сообщение принято. Обратитесь в полицию (102) или горячую линию (8-800-2000-122).",
        reply_markup=user_menu()
    )
    await state.clear()

@router.message(UserStates.AskQuestion)
async def handle_question(message: types.Message, state: FSMContext):
    """Handle user-submitted questions for experts."""
    user_id = message.from_user.id
    question = message.text
    data = read_data()
    data.setdefault('questions', []).append({
        'id': str(uuid.uuid4()),
        'user_id': user_id,
        'question': question,
        'status': 'Новое'
    })
    write_data(data)
    await message.answer("Ваш вопрос отправлен экспертам!", reply_markup=user_menu())
    await state.clear()

@router.message(UserStates.AddEvent)
async def handle_add_event(message: types.Message, state: FSMContext):
    """Handle admin addition of events to the system."""
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
            data.setdefault('events', []).append({
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

@router.message(UserStates.AddAdmin)
async def handle_add_admin(message: types.Message, state: FSMContext):
    """Handle admin addition of new admin Telegram IDs."""
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
            if new_admin_id not in data.get('admins', []):
                data.setdefault('admins', []).append(new_admin_id)
                added_count += 1
            else:
                existing_admins.append(str(new_admin_id))
        except ValueError:
            error_messages.append(f"Ошибка: {admin_id} не является числовым Telegram ID.")

    if added_count > 0:
        write_data(data)
        response = f"Успешно добавлено {added_count} администратор(ов)!"
    else:
        response = "Ни один администратор не добавлено"