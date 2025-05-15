from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from reqwest import get_barbers, get_services
from aiogram import Bot, Dispatcher, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import Command, StateFilter, CommandStart
from aiogram.fsm.storage.memory import MemoryStorage
import logging
import asyncio
from aiogram import Bot, Dispatcher, F
from dispecher1 import dp
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, Message, CallbackQuery

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