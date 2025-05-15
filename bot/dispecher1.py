import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from states import Work
from weather import How_weather
from aiogram.fsm.context import FSMContext
from generators import generate
from database import Work_AI_dict, ContexManager, Work_weather
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, \
    KeyboardButton
from geopy.distance import geodesic
from aiogram import F
from aiogram.types import Message
import requests
from io import BytesIO
from aiogram.types import InputFile
import os
from PIL import Image, ImageDraw, ImageFont
from typing import Optional

dp = Dispatcher()
bot = Bot(token="7699700109:AAHk-ntwf8EuhRA5eDXaJXyqGq9F-v0OZHo")

dict_Work_AI = Work_AI_dict()
contant = ContexManager()
weather_work = Work_weather()

markup = ReplyKeyboardMarkup(
    keyboard=[
        [types.KeyboardButton(text="Запустить нейросеть ✨")],
        [types.KeyboardButton(text="Выключить нейросеть ❌")],
        [types.KeyboardButton(text="Узнать погоду ❄")],
        [types.KeyboardButton(text="Инструкция")],
        [KeyboardButton(text="🖼 Создать мем")],
        [types.KeyboardButton(text="📤 Загрузить фото")],
        [types.KeyboardButton(text="Ближайшие медпункты", request_location=True)]
    ],
    resize_keyboard=True
)

# Константы для Yandex Maps
YANDEX_STATIC_MAPS_URL = "https://static-maps.yandex.ru/v1"
YANDEX_MAPS_API_KEY = "f3a0fe3a-b07e-4840-a1da-06f18b2ddf13"

# Создаем необходимые директории
os.makedirs("user_images", exist_ok=True)
os.makedirs("memes", exist_ok=True)
os.makedirs("user_documents", exist_ok=True)


@dp.message(CommandStart())
async def cmd_start(message: Message):
    try:
        dict_Work_AI.add_message(message.chat.id, False)
        contant.clear(message.chat.id)
        weather_work.add_message(message.chat.id, False)
        await bot.send_message(
            message.chat.id,
            text="Привет! ❤ Я буду вашим ассистентом. Могу помочь вам с поиском интересных мест! 🙌",
            reply_markup=markup
        )
    except KeyboardInterrupt:
        print("бот выключен")


async def generate_static_map(lat: float, lon: float, medical_points: list):
    markers = [f"color:red~{lat},{lon}"]  # Метка пользователя
    for point in medical_points:
        markers.append(f"color:blue~{point['lat']},{point['lon']}")

    params = {
        "apikey": YANDEX_MAPS_API_KEY,
        "ll": f"{lon},{lat}",
        "spn": "0.05,0.05",
        "l": "map",
        "pt": "~".join(markers),
        "size": "650,450"
    }

    try:
        response = requests.get(YANDEX_STATIC_MAPS_URL, params=params)
        if response.status_code == 200:
            return BytesIO(response.content)
        return None
    except Exception as e:
        print(f"Ошибка генерации карты: {e}")
        return None


async def get_nearest_medical(latitude: float, longitude: float, radius_km: int = 200):
    url = "https://search-maps.yandex.ru/v1/"
    params = {
        "apikey": YANDEX_MAPS_API_KEY,
        "text": "больница, поликлиника, медпункт",
        "lang": "ru_RU",
        "ll": f"{longitude},{latitude}",
        "spn": f"{radius_km / 300},{radius_km / 300}",
        "type": "biz",
        "results": 5
    }

    try:
        response = requests.get(url, params=params).json()
        medical_points = []

        for item in response.get("features", []):
            name = item["properties"]["name"]
            address = item["properties"]["description"]
            point_lon, point_lat = item["geometry"]["coordinates"]
            distance = geodesic((latitude, longitude), (point_lat, point_lon)).km

            medical_points.append({
                "name": name,
                "address": address,
                "distance": round(distance, 2),
                "lat": point_lat,
                "lon": point_lon
            })

        return sorted(medical_points, key=lambda x: x["distance"])
    except Exception as e:
        print(f"Ошибка запроса к Yandex.Maps: {e}")
        return []


def generate_yandex_map_link(lat: float, lon: float, points: list):
    markers = [f"{lat},{lon},pm2rdl"]
    for point in points:
        markers.append(f"{point['lat']},{point['lon']},pm2bll")

    link = (
        f"https://yandex.ru/maps/?mode=search&text={lat}%2C{lon}"
        f"&pt={'~'.join(markers)}"
    )
    return link


@dp.message(F.location)
async def handle_location(message: Message):
    lat = message.location.latitude
    lon = message.location.longitude

    medical_points = await get_nearest_medical(lat, lon)
    if not medical_points:
        await message.answer("🚨 Рядом не найдено медпунктов.")
        return

    response_text = ["📍 Ближайшие медпункты:"]
    for idx, point in enumerate(medical_points, 1):
        response_text.append(
            f"\n{idx}. **{point['name']}**\n"
            f"   🏥 Адрес: {point['address']}\n"
            f"   📏 Расстояние: {point['distance']} км"
        )

    map_link = generate_yandex_map_link(lat, lon, medical_points)
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🗺️ Открыть карту", url=map_link)]
        ]
    )

    map_image = await generate_static_map(lat, lon, medical_points)
    if map_image:
        await message.answer_photo(
            InputFile(map_image, filename="map.jpg"),
            caption="\n".join(response_text),
            reply_markup=keyboard
        )
    else:
        await message.answer("\n".join(response_text), reply_markup=keyboard)


@dp.message(Command("go"))
async def cmd_go(message: Message):
    await message.answer('Нейросеть запущена')
    dict_Work_AI.add_message(message.chat.id, True)


@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer("""/go - запустить нейросеть
/stop - остановить нейросеть
/weather - узнать погоду
/help - инструкция
/start - запуск чат-бота
МЕНЮ для создания мема:
1. Кнопка загрузить фото
2. Скидываете фото
3. Кнопка создать мем
4. Ввести подпись для фото
МЕНЮ для медпунктов:
Разрешаем отправление геопозиции и ожидаем ссылку на маршрут""")


@dp.message(Command("stop"))
async def cmd_stop(message: Message):
    await message.answer('Нейросеть отключена')
    dict_Work_AI.add_message(message.chat.id, False)
    contant.clear(message.chat.id)


@dp.message(Command("weather"))
async def cmd_weather(message: Message):
    weather_work.add_message(message.chat.id, True)
    dict_Work_AI.add_message(message.chat.id, False)
    await message.answer(How_weather())


async def get_last_user_photo(user_id: int) -> Optional[str]:
    try:
        import glob
        user_files = glob.glob(f"user_images/{user_id}_*.jpg")
        if not user_files:
            return None
        user_files.sort(key=os.path.getmtime, reverse=True)
        return user_files[0]
    except Exception as e:
        print(f"Ошибка при поиске фото: {e}")
        return None


async def create_meme(image_path: str, text: str) -> str:
    try:
        with Image.open(image_path) as img:
            draw = ImageDraw.Draw(img)

            try:
                font = ImageFont.truetype("arial.ttf", size=40)
            except:
                font = ImageFont.load_default(size=40)

            text_width = draw.textlength(text, font=font)
            x = (img.width - text_width) / 2
            y = 10

            draw.text(
                (x, y),
                text,
                fill="white",
                font=font,
                stroke_width=2,
                stroke_fill="black"
            )

            meme_path = f"memes/{os.path.basename(image_path)}"
            img.save(meme_path)
            return meme_path
    except Exception as e:
        print(f"Ошибка при создании мема: {e}")
        return None


@dp.message(F.text.startswith("Мем:"))
async def make_meme(message: Message):
    last_photo = await get_last_user_photo(message.from_user.id)
    if not last_photo:
        await message.answer("❌ Сначала отправьте мне фото!")
        return

    meme_text = message.text.split("Мем:")[1].strip()
    if not meme_text:
        await message.answer("❌ Добавьте текст после 'Мем:'")
        return

    meme_path = await create_meme(last_photo, meme_text)
    if meme_path:
        with open(meme_path, 'rb') as photo:
            await message.answer_photo(
                photo,
                caption="Ваш мем готов! 🎉"
            )
    else:
        await message.answer("❌ Не удалось создать мем")


@dp.message(F.text == "🖼 Создать мем")
async def ask_for_meme_text(message: Message, state: FSMContext):
    last_photo = await get_last_user_photo(message.from_user.id)
    if not last_photo:
        await message.answer("❌ Сначала загрузите фото через кнопку '📤 Загрузить фото'")
        return

    await state.update_data(photo_path=last_photo)
    await message.answer(
        "✏ Введите текст для мема (можно просто текст без 'Мем:')",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="❌ Отменить создание мема")]],
            resize_keyboard=True
        )
    )
    await state.set_state(Work.waiting_for_meme_text)


@dp.message(Work.waiting_for_meme_text, F.text == "❌ Отменить создание мема")
async def cancel_meme_creation(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Создание мема отменено", reply_markup=markup)


@dp.message(Work.waiting_for_meme_text)
async def process_meme_text(message: Message, state: FSMContext):
    # Проверка на команды
    if message.text in ["Запустить нейросеть ✨", "Выключить нейросеть ❌", "Узнать погоду ❄", "Инструкция"]:
        await state.clear()
        await ai(message)
        return

    user_data = await state.get_data()
    photo_path = user_data.get('photo_path')

    if not photo_path or not os.path.exists(photo_path):
        await message.answer("❌ Фото не найдено. Пожалуйста, загрузите фото снова.")
        await state.clear()
        return

    meme_text = message.text.replace("Мем:", "").strip()
    if not meme_text:
        await message.answer("❌ Текст для мема не может быть пустым")
        return

    try:
        # Создаем мем
        meme_path = await create_meme(photo_path, meme_text)
        if not meme_path or not os.path.exists(meme_path):
            raise FileNotFoundError("Мем не был создан")

        # Открываем файл в бинарном режиме и отправляем
        with open(meme_path, 'rb') as photo_file:
            # Создаем BytesIO объект для отправки
            photo_bytes = BytesIO(photo_file.read())
            photo_bytes.seek(0)  # Важно: переводим указатель в начало

            await message.answer_photo(
                types.BufferedInputFile(photo_bytes.read(), filename="meme.jpg"),
                caption="Ваш мем готов! 🎉",
                reply_markup=markup
            )

    except Exception as e:
        print(f"Ошибка при создании/отправке мема: {str(e)}")
        await message.answer(
            "❌ Произошла ошибка при создании мема. Попробуйте еще раз.",
            reply_markup=markup
        )
    finally:
        await state.clear()


@dp.message(F.photo)
async def handle_photo(message: Message):
    photo = message.photo[-1]
    file_id = photo.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path

    original_path = f"user_images/{message.from_user.id}_{file_id}.jpg"
    await bot.download_file(file_path, original_path)

    await message.answer("Фото сохранено! Теперь вы можете создать мем, нажав кнопку '🖼 Создать мем'")


@dp.message(F.document & (F.document.mime_type.startswith('image/')))
async def handle_image_doc(message: Message):
    file_id = message.document.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path

    save_path = f"user_images/{message.from_user.id}_{file_id}.jpg"
    await bot.download_file(file_path, save_path)

    await message.answer("Изображение сохранено! Теперь вы можете создать мем, нажав кнопку '🖼 Создать мем'")


@dp.message()
async def ai(message: Message):
    if message.text == 'Узнать погоду ❄':
        await message.answer(How_weather())
    elif message.text == 'Запустить нейросеть ✨':
        await message.answer('Нейросеть запущена')
        dict_Work_AI.add_message(message.chat.id, True)
    elif message.text == 'Выключить нейросеть ❌':
        await message.answer('Нейросеть отключена')
        contant.clear(message.chat.id)
        dict_Work_AI.add_message(message.chat.id, False)
    elif message.text == 'Инструкция':
        await message.answer("""/go - запустить нейросеть
/stop - остановить нейросеть
/weather - узнать погода""")
    elif dict_Work_AI.Work_Ai_message(message.chat.id):
        contant.add_message(message.chat.id, message.text)
        res = await generate(contant.contex_message(message.chat.id))
        await message.answer(res.choices[0].message.content)
    elif weather_work.Work_weather_message(message.chat.id):
        weather_work.add_message(message.chat.id, False)
        await message.answer(How_weather())


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass