
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from dispecher1 import dp


@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    kb = [
        [
            types.KeyboardButton(text="Запустить нейросеть ✨"),
            types.KeyboardButton(text="Выключить нейросеть ❌")
        ],
        [
            types.KeyboardButton(text="Узнать погоду ❄"),
            types.KeyboardButton(text="Инструкция 📝")
        ],
        [
            types.KeyboardButton(text="📤 Загрузить фото"),
            types.KeyboardButton(text="📍 Ближайшие медпункты", request_location=True)
        ]
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Выберите действие"
    )
    await message.answer("Главное меню:", reply_markup=keyboard)