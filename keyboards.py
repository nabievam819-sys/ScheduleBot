from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


DAYS = [
    "Понедельник",
    "Вторник",
    "Среда",
    "Четверг",
    "Пятница",
    "Суббота",
    "Воскресенье"
]


def main_menu():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="➕ Добавить занятие"),
                KeyboardButton(text="📋 Всё расписание")
            ],
            [
                KeyboardButton(text="📅 Расписание по дню"),
                KeyboardButton(text="🗑 Удалить занятие")
            ]
        ],
        resize_keyboard=True
    )

    return keyboard


def days_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Понедельник"),
                KeyboardButton(text="Вторник")
            ],
            [
                KeyboardButton(text="Среда"),
                KeyboardButton(text="Четверг")
            ],
            [
                KeyboardButton(text="Пятница"),
                KeyboardButton(text="Суббота")
            ],
            [
                KeyboardButton(text="Воскресенье")
            ]
        ],
        resize_keyboard=True
    )

    return keyboard


def delete_keyboard(lessons):
    builder = InlineKeyboardBuilder()

    for lesson in lessons:
        lesson_id, day, subject, time, room = lesson

        builder.button(
            text=f"{time} | {subject} | каб. {room}",
            callback_data=f"delete:{lesson_id}"
        )

    builder.adjust(1)

    return builder.as_markup()
