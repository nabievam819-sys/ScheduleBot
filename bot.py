import asyncio
import os

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from dotenv import load_dotenv

from database import (
    create_table,
    add_lesson,
    get_all_lessons,
    get_lessons_by_day,
    delete_lesson
)

from keyboards import (
    main_menu,
    days_keyboard,
    delete_keyboard,
    DAYS
)

from states import AddLessonStates


load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в файле .env")


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# =========================
# /start
# =========================

@dp.message(CommandStart())
async def start_command(message: Message, state: FSMContext):
    await state.clear()

    await message.answer(
        "👋 Привет!\n\n"
        "Я бот для хранения расписания.\n"
        "Выбери нужное действие ниже 👇",
        reply_markup=main_menu()
    )


# =========================
# /help
# =========================

@dp.message(Command("help"))
async def help_command(message: Message):
    await message.answer(
        "📚 Возможности бота:\n\n"
        "➕ Добавить занятие\n"
        "📋 Всё расписание\n"
        "📅 Расписание по дню\n"
        "🗑 Удалить занятие\n\n"
        "Используй кнопки главного меню."
    )


# =========================
# ДОБАВЛЕНИЕ ЗАНЯТИЯ
# =========================

@dp.message(F.text == "➕ Добавить занятие")
async def add_start(message: Message, state: FSMContext):
    await state.set_state(AddLessonStates.day)

    await message.answer(
        "📅 Выберите день недели:",
        reply_markup=days_keyboard()
    )


# =========================
# ВЫБОР ДНЯ ПРИ ДОБАВЛЕНИИ
# =========================

@dp.message(AddLessonStates.day)
async def add_day(message: Message, state: FSMContext):

    if message.text not in DAYS:
        await message.answer(
            "❗ Пожалуйста, выберите день кнопкой."
        )
        return

    await state.update_data(day=message.text)

    await state.set_state(AddLessonStates.subject)

    await message.answer(
        "📚 Введите название предмета:",
    )


# =========================
# ВВОД ПРЕДМЕТА
# =========================

@dp.message(AddLessonStates.subject)
async def add_subject(message: Message, state: FSMContext):

    subject = message.text.strip()

    if not subject:
        await message.answer(
            "❗ Название предмета не может быть пустым."
        )
        return

    await state.update_data(subject=subject)

    await state.set_state(AddLessonStates.time)

    await message.answer(
        "⏰ Введите время занятия.\n\n"
        "Например:\n"
        "09:00"
    )


# =========================
# ВВОД ВРЕМЕНИ
# =========================

@dp.message(AddLessonStates.time)
async def add_time(message: Message, state: FSMContext):

    time = message.text.strip()

    if not time:
        await message.answer(
            "❗ Время не может быть пустым."
        )
        return

    await state.update_data(time=time)

    await state.set_state(AddLessonStates.room)

    await message.answer(
        "🚪 Введите номер кабинета.\n\n"
        "Например:\n"
        "301"
    )


# =========================
# ВВОД КАБИНЕТА
# =========================

@dp.message(AddLessonStates.room)
async def add_room(message: Message, state: FSMContext):

    room = message.text.strip()

    if not room:
        await message.answer(
            "❗ Кабинет не может быть пустым."
        )
        return

    data = await state.get_data()

    day = data["day"]
    subject = data["subject"]
    time = data["time"]

    add_lesson(
        day=day,
        subject=subject,
        time=time,
        room=room
    )

    await state.clear()

    await message.answer(
        "✅ Занятие успешно добавлено!\n\n"
        f"📅 День: {day}\n"
        f"📚 Предмет: {subject}\n"
        f"⏰ Время: {time}\n"
        f"🚪 Кабинет: {room}",
        reply_markup=main_menu()
    )


# =========================
# ВСЁ РАСПИСАНИЕ
# =========================

@dp.message(F.text == "📋 Всё расписание")
async def show_all_schedule(message: Message):

    lessons = get_all_lessons()

    if not lessons:
        await message.answer(
            "📭 Расписание пока пустое."
        )
        return

    text = "📚 ВСЁ РАСПИСАНИЕ\n\n"

    current_day = None

    for lesson in lessons:
        lesson_id, day, subject, time, room = lesson

        if day != current_day:
            text += f"📅 <b>{day}</b>\n"
            current_day = day

        text += (
            f"⏰ {time} — "
            f"{subject} — "
            f"каб. {room}\n"
        )

    await message.answer(
        text,
        parse_mode="HTML"
    )


# =========================
# РАСПИСАНИЕ ПО ДНЮ
# =========================

@dp.message(F.text == "📅 Расписание по дню")
async def choose_day(message: Message):

    await message.answer(
        "📅 Выберите день:",
        reply_markup=days_keyboard()
    )


@dp.message(F.text.in_(DAYS))
async def show_day_schedule(message: Message):

    lessons = get_lessons_by_day(message.text)

    if not lessons:
        await message.answer(
            f"📭 В день «{message.text}» занятий нет.",
            reply_markup=main_menu()
        )
        return

    text = f"📅 <b>{message.text}</b>\n\n"

    for lesson in lessons:
        lesson_id, day, subject, time, room = lesson

        text += (
            f"⏰ {time}\n"
            f"📚 {subject}\n"
            f"🚪 Кабинет: {room}\n\n"
        )

    await message.answer(
        text,
        parse_mode="HTML",
        reply_markup=main_menu()
    )


# =========================
# УДАЛЕНИЕ ЗАНЯТИЯ
# =========================

@dp.message(F.text == "🗑 Удалить занятие")
async def delete_start(message: Message):

    lessons = get_all_lessons()

    if not lessons:
        await message.answer(
            "📭 Расписание пустое. Удалять нечего."
        )
        return

    await message.answer(
        "🗑 Выберите занятие, которое хотите удалить:",
        reply_markup=delete_keyboard(lessons)
    )


# =========================
# ОБРАБОТКА УДАЛЕНИЯ
# =========================

@dp.callback_query(F.data.startswith("delete:"))
async def delete_callback(callback: CallbackQuery):

    lesson_id = int(
        callback.data.split(":")[1]
    )

    delete_lesson(lesson_id)

    await callback.answer(
        "Занятие удалено!"
    )

    await callback.message.edit_text(
        "✅ Занятие успешно удалено."
    )


# =========================
# НЕИЗВЕСТНЫЕ СООБЩЕНИЯ
# =========================

@dp.message()
async def unknown_message(message: Message):

    await message.answer(
        "❓ Я не понял команду.\n\n"
        "Используй кнопки меню 👇",
        reply_markup=main_menu()
    )


# =========================
# ЗАПУСК БОТА
# =========================

async def main():

    create_table()

    print("🤖 ScheduleBot запущен!")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
