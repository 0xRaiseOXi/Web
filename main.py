import asyncio
import logging
from random import randint
import time
from aiogram import F, Bot, types, Dispatcher
from aiogram.filters.command import Command 
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import copy
import pymongo
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import FSInputFile, URLInputFile, BufferedInputFile
from aiogram.enums import ParseMode
from aiogram import html
from aiogram.types.web_app_info import WebAppInfo

db_client = pymongo.MongoClient("mongodb://localhost:27017/")
current_db = db_client["OXI"]

collection = current_db["OXI_tokens"]
collection2 = current_db["OXI_improvements"]

data_user = {
    "_id": "telegram_id",
    "user_name": "",
    "oxi_tokens_value": 0,
    "x_factor": 0,
    "vault_size": 0,
    "last_time_update": 0,
    "vault_use": 0,
    "last_update_vault": 0,
    "planet": "",
    "miners": {
        "slot_1": {
            "level": 1
        },
        "slot_2": {
            "level": 0
        },
    }
}

data_user_improvements = {
    "_id": "telegram_id",
    "storage": 1,
    "vault": 1
}


vault_size_CONSTANT = {
    1: 5000,
    2: 12000,
    3: 50000,
    4: 120000,
    5: 450000,
    6: 800000,
    7: 1600000,
    8: 3500000,
    9: 5000000,
    10: 10000000
}

vault_size_CONSTANT_View = {
    1: "5k",
    2: "12k",
    3: "50k",
    4: "120k",
    5: "450k",
    6: "800k",
    7: "1.6M",
    8: "3.5M",
    9: "5M",
    10: "10M"
}

miners_size = {
    1: 1000,
    2: 3500,
    3: 8000,
    4: 12000,
    5: 15000
}

logging.basicConfig(level=logging.INFO)
bot = Bot(token='7404195116:AAGs7cz3VhBp3T8E4I5KxXhdWmIsXeYEITM')
dp = Dispatcher()

async def update_tokens_value_vault(id):
    data = collection.find_one({'_id': id})
    data_user_2 = collection2.find_one({'_id': id})
    last_time_update = data['last_time_update']
    current_time = time.time() 
    time_difference = current_time - last_time_update
    time_different_in_hours = time_difference / 3600
    added_tokens = int(time_different_in_hours * 1000)
    vault_size = int(vault_size_CONSTANT[data_user_2['vault']])
    if added_tokens > vault_size:
        return vault_size
    return added_tokens

def get_main_menu_text(user_name, tokens_value, tokens_in_vault, vault_level, vault_use):
    text = f"Главное меню управления базой игрока {user_name}\n\n================================\n<b>💰 Токенов OXI: {tokens_value}</b>\n================================\n\nХранилище: {tokens_in_vault}/{vault_size_CONSTANT_View[vault_level]} OXI ({vault_use}%)\n\nМайнеров: 1 (+1000 OXI/hour)\nДобыча: 0\nЭнергия: 20е/100е\nЩит: 100%"
    return text

async def main_menu(callback: types.CallbackQuery = None, message: types.Message = None):
    buttons = [
         [
            types.InlineKeyboardButton(text="Майнеры (1/8)", callback_data="miners_main"),
            types.InlineKeyboardButton(text="Задания (0)", callback_data="tasks")
        ],
        [
            types.InlineKeyboardButton(text="Склад", callback_data="storage"),
            types.InlineKeyboardButton(text="Рынок", callback_data="market"),
            types.InlineKeyboardButton(text="Добыча", callback_data="mining_resources")
        ],
        [
            types.InlineKeyboardButton(text="<-- Собрать OXI -->", callback_data="collect_tokens"),
            types.InlineKeyboardButton(text="Обновить", callback_data="main_menu_update"),
            types.InlineKeyboardButton(text="Открыть", web_app=WebAppInfo(url="https://oxiprotocol.ru/"))
        ],
        [
            types.InlineKeyboardButton(text="Профиль", callback_data="profile"),
            types.InlineKeyboardButton(text="Лига", callback_data="league"),
            types.InlineKeyboardButton(text="Энергия", callback_data="energy")
        ],
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)

    if callback:
        data_user = collection.find_one({"_id": callback.from_user.id})
        data_user_2 = collection2.find_one({"_id": callback.from_user.id})
        tokens_in_vault = await update_tokens_value_vault(callback.from_user.id)
        vault_use = int(tokens_in_vault / vault_size_CONSTANT[data_user_2['vault']] * 100)
        media = types.InputMediaPhoto(media="AgACAgIAAxkDAANAZlXF6Ly5ibqeNZCy1yw53K3BTL8AAhjZMRtSo7BKJXFKHkFNrvUBAAMCAAN4AAM1BA", caption=get_main_menu_text(data_user['user_name'], data_user['oxi_tokens_value'], tokens_in_vault, data_user_2['vault'], vault_use), parse_mode=ParseMode.HTML)
        await callback.message.edit_media(media=media, reply_markup=keyboard)
    else:
        data_user = collection.find_one({"_id": message.from_user.id})
        data_user_2 = collection2.find_one({"_id": message.from_user.id})
        tokens_in_vault = await update_tokens_value_vault(message.from_user.id)
        vault_use = int(tokens_in_vault / vault_size_CONSTANT[data_user_2['vault']] * 100)
        await message.answer_photo("AgACAgIAAxkDAANAZlXF6Ly5ibqeNZCy1yw53K3BTL8AAhjZMRtSo7BKJXFKHkFNrvUBAAMCAAN4AAM1BA", caption=get_main_menu_text(data_user['user_name'], data_user['oxi_tokens_value'], tokens_in_vault, data_user_2['vault'], vault_use), reply_markup=keyboard, parse_mode=ParseMode.HTML)

"AgACAgIAAxkDAAM-ZlXFiRk_cYexryJIYktkDdHebn8AAhbZMRtSo7BKhqxWN751XAcBAAMCAAN4AAM1BA"
"AgACAgIAAxkDAANAZlXF6Ly5ibqeNZCy1yw53K3BTL8AAhjZMRtSo7BKJXFKHkFNrvUBAAMCAAN4AAM1BA"

# @dp.message(Command('images'))
# async def load(message: types.Message):
#     file_ids = []
#     image_from_pc = FSInputFile("output.png")
#     result = await message.answer_photo(
#         image_from_pc,
#         caption="Изображение из файла на компьютере"
#     )
#     file_ids.append(result.photo[-1].file_id)
#     print(file_ids)

@dp.callback_query(F.data == ("miners_main"))
async def get_storage(callback: types.CallbackQuery):
    buttons = []
    data_user = collection.find_one({"_id": callback.from_user.id})
    buttons_add = []
    for slot, data_miner in data_user['miners'].items():
        if len(buttons_add) == 2:
            buttons.append(buttons_add)
            buttons_add.clear()
        text_button = "Майнер " + slot.split("_")[1]
        buttons_add.append(types.InlineKeyboardButton(text=text_button, callback_data=f"miner_{slot.split("_")[1]}"))
    if len(buttons_add) != 0:
        buttons.append(buttons_add)
    buttons.append(types.InlineKeyboardButton(text="<-- Назад", callback_data="main_menu_update"))
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    text = f"Майнеры 1/8"
    media = types.InputMediaPhoto(media="AgACAgIAAxkDAANAZlXF6Ly5ibqeNZCy1yw53K3BTL8AAhjZMRtSo7BKJXFKHkFNrvUBAAMCAAN4AAM1BA", caption=text, parse_mode=ParseMode.HTML)
    await callback.message.edit_media(media=media, reply_markup=keyboard)

@dp.callback_query(F.data == ("storage"))
async def get_storage(callback: types.CallbackQuery):
    buttons = [
        [types.InlineKeyboardButton(text="<-- Назад", callback_data="main_menu_update")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    text = f"Склад 0/1000 (Уровень 1)\n\nНа складе хранятся ваши майнеры, добывающие оборудование и добытые ресурсы. Здесь же можно улучшить любые устройства."
    media = types.InputMediaPhoto(media="AgACAgIAAxkDAANAZlXF6Ly5ibqeNZCy1yw53K3BTL8AAhjZMRtSo7BKJXFKHkFNrvUBAAMCAAN4AAM1BA", caption=text, parse_mode=ParseMode.HTML)
    await callback.message.edit_media(media=media, reply_markup=keyboard)

@dp.callback_query(F.data == ("collect_tokens"))
async def collect_tokens(callback: types.CallbackQuery):
    added_tokens = await update_tokens_value_vault(callback.from_user.id)
    data = collection.find_one({'_id': callback.from_user.id})
    data['oxi_tokens_value'] += added_tokens
    data['last_time_update'] = time.time()
    new_data = collection.replace_one({'_id': callback.from_user.id}, data)
    print(new_data)
    buttons = [
        [
            types.InlineKeyboardButton(text="Подтвердить", callback_data="main_menu")
        ],
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    media = types.InputMediaPhoto(media="AgACAgIAAxkDAANAZlXF6Ly5ibqeNZCy1yw53K3BTL8AAhjZMRtSo7BKJXFKHkFNrvUBAAMCAAN4AAM1BA", caption=f"Токенов зачислено: {added_tokens}")
    await callback.message.edit_media(media=media, reply_markup=keyboard)

@dp.callback_query(F.data == ("main_menu_update"))
async def get_main_menu_update(callback: types.CallbackQuery):
    try:
        await main_menu(callback=callback)
    except TelegramBadRequest:
        pass
     
@dp.callback_query(F.data == ("main_menu"))
async def get_market(callback: types.CallbackQuery):
	await main_menu(callback=callback)


@dp.callback_query(F.data == ("market"))
async def get_market(callback: types.CallbackQuery):
     pass

@dp.callback_query(F.data == ("mining_resources"))
async def get_mining_resources(callback: types.CallbackQuery):
     pass

@dp.callback_query(F.data == ("profile"))
async def get_profile(callback: types.CallbackQuery):
    buttons = [
        [
            types.InlineKeyboardButton(text="Управление токенами", callback_data="num_finish")
        ],
        [
            types.InlineKeyboardButton(text="<-- Назад", callback_data="main_menu_update")
        ]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    data = collection.find_one({'_id': callback.from_user.id})
    text = f"Профиль игрока {data['user_name']}\n\nID: {data['_id']}\n\nРефералов: 0\nБонус за реферала: +5000 OXI\nVIP: 1\n\nГруппа: None\nЛига: Bronze"
    media = types.InputMediaPhoto(media="AgACAgIAAxkDAANAZlXF6Ly5ibqeNZCy1yw53K3BTL8AAhjZMRtSo7BKJXFKHkFNrvUBAAMCAAN4AAM1BA", caption=text)
    await callback.message.edit_media(media=media, reply_markup=keyboard)

@dp.callback_query(F.data == ("league"))
async def get_league(callback: types.CallbackQuery):
     pass

@dp.callback_query(F.data == ("energy"))
async def get_energy(callback: types.CallbackQuery):
     pass


@dp.callback_query(F.data == ("improvements"))
async def get_storage(callback: types.CallbackQuery):
    buttons = [
        [
            types.InlineKeyboardButton(text="-->", callback_data="improvements_vault")
        ],
        [
            types.InlineKeyboardButton(text="Улучшить", callback_data="num_finish")
        ],
        [
            types.InlineKeyboardButton(text="<-- Назад", callback_data="main_menu_update")
        ]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback.message.edit_caption(caption=f"Склад Уровень 1.\n\nТребуемые ресурсы для улучшения: ", reply_markup=keyboard)

@dp.callback_query(F.data == ("improvements_vault"))
async def get_storage(callback: types.CallbackQuery):
    buttons = [
        [
            types.InlineKeyboardButton(text="<--", callback_data="improvements"),
            types.InlineKeyboardButton(text="-->", callback_data="num_finish")
        ],
        [
            types.InlineKeyboardButton(text="Улучшить", callback_data="num_finish")
        ],
        [
            types.InlineKeyboardButton(text="<-- Назад", callback_data="num_finish")
        ]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    data = collection2.find_one({'_id': callback.from_user.id})
    await callback.message.edit_caption(caption=f"Хранилище Уровень {data['vault']}.\n\nТребуемые ресурсы для улучшения: 10000 OXI", reply_markup=keyboard)


"Улучшения -> Меню с кнопками <- -> И возможностью выюора любого устройства для улучшения. Требуются в оснвном тоены OXI + ресурсы. Можно покупать premium"
"Профиль -> Управленпие токенами -> Перевести, сжечь"

@dp.message((Command("start")))
async def start(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Начинаем!",
        callback_data="start_main")
    )
    user = collection.find_one({"_id": message.from_user.id})
    if user == None:
        await message.answer("""Добро пожаловать в OXI Protocol!\n\nЗдесь вас ждет самые необычные и бурные игры. Выбирайте планету, создавайте базу и участвуйте во всех мероприятиях - объединяйтесь, нападайте, устраивайте войны, стройте фабрики или помогайте другим участникам.\nСейчас 1 стадия проекта - активный майнинг. Майните токены, добывайте ресурсы и продавайте их на внутреннем рынке. \nСамые активные участники могут приобрести premium-ресурсы, но вся экономика построена так, что ускоряется только игровой процесс, но не получается преобладание перед другими игроками.\n\nТокен OXI - основная игровая валюта. Позже, добытые токены, бонусы, полученные NFT будут сконвертированы в настоящие токены OXI.""", reply_markup=builder.as_markup())
        data_user = {
            "_id": message.from_user.id,
            "user_name": message.from_user.first_name,
            "oxi_tokens_value": 0,
            "x_factor": 1,
            "vault_size": 5000,
            "last_time_update": time.time(),
            "last_update_vault": 0,
            "planet": None,
            "miners": {
                "slot_1": {
                    "level": 1
                },
                "slot_2": {
                    "level": 0
                },
            }
        }
        collection.insert_one(data_user)

        data_user_improvements = {
            "_id": message.from_user.id,
            "storage": 1,
            "vault": 1
        }
        collection2.insert_one(data_user_improvements)
    else:
        await main_menu(message=message)


async def planet_xr_1(callback: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="XR-2 -->",
        callback_data="XR-2")
    )
    builder.add(types.InlineKeyboardButton(
        text="Выбрать",
        callback_data="XR-1-OK")
    )
    await callback.message.edit_text("""Отлично! Теперь выберем территорию, где будет расположена база.\n\nПланета XR-1.\n\nНа этой планете все хорошо и стабильно, температура и атмосфера в норме. Здесь вы в безопасности. Ваша задача самая главная - добывать ресурсы и продавать их на межпланетарном рынке. Игроки других планет без вас не справятся!\n\n- Максимальный множитель токенов: x1\n- Атмосфера: стабильна (-20C | +20C)\nВойны: Запрещены\n\nРасположение базы в будущем можно изменить.""", reply_markup=builder.as_markup())

async def planet_xr_2(callback: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="<-- XR-1",
        callback_data="XR-1")
    )
    builder.add(types.InlineKeyboardButton(
        text="XR-3 -->",
        callback_data="XR-3")
    )
    builder.add(types.InlineKeyboardButton(
        text="Выбрать",
        callback_data="XR-2-OK")
    )
    await callback.message.edit_text("""Отлично! Теперь выберем территорию, где будет расположена база.\n\nПланета XR-2.\n\nКрайне неспокойная планета. Температура, погода и атмосфера часто выводят из строя всю вашу базу. Здесь макисмальная активность ядра планеты - энергии неограниченное количество. Нападения разрешены, но строго ограничены правилами.
Ваша задача - строить фабрики, которые требуют огромное количество энергии и производить нужные товары из ресурсов, которые требуются всем учатникам.\n\n- Максимальный множитель токенов: x5.\nАтмосфера: нестабильна (-100C | +150C)\Войны: разрешены, но ограничены\n\nРасположение базы в будущем можно изменить.""", reply_markup=builder.as_markup())

async def planet_xr_3(callback: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="<-- XR-2",
        callback_data="XR-2")
    )
    builder.add(types.InlineKeyboardButton(
        text="Выбрать",
        callback_data="XR-3-OK")
    )
    await callback.message.edit_text("""Отлично! Теперь выберем территорию, где будет расположена база.\n\nПланета XR-3 или Полный Хаос.\n\nЗдесь творится полный хаос и разруха. Базы еле держаться. Энергии нет совсем, прихожится получать ее из любых доступных источников.
Нападения, войны, удары разрешены - никаких правил. Ресурсы крайне ограничены, придется запупать на внутреннем рынке или добывать войной. Постоянные перегрузки отключают все майнеры - вы вынуждены 
восстанавливать их работу. Максимальный размер хранилища майнера ограничен.\n\n- Максимальный множитель токенов: x100\n- Атмосфера: крайне нестабильна\n- Войны: разрешены, правил нет\n\nРасположение базы в будущем можно изменить.""", reply_markup=builder.as_markup())

async def main_start(callback: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Продолжить -->",
        callback_data="Main-Start")
    )
    await callback.message.edit_text("""Стадия 1. Активный майнинг.\n\nФух! Вроде добрались. Мы на планете {}, здесь крайне... Передаю полный контроль тебе!\n\nРекомендуем как можно больше улучшать базу, тратить и сжигать токены OXI.\n\nТолько тебе решать, по каким правилам ты играешь. Удачной игры!""", reply_markup=builder.as_markup())


async def planet_xr_1_ok(callback: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Старт!",
        callback_data="XR-1-OK-MAIN")
    )
    builder.add(types.InlineKeyboardButton(
        text="<-- Назад",
        callback_data="XR-1")
    )
    await callback.message.edit_text("""Вы выбираете планету XR-1.""", reply_markup=builder.as_markup())

async def planet_xr_2_ok(callback: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Старт!",
        callback_data="XR-2-OK-MAIN")
    )
    builder.add(types.InlineKeyboardButton(
        text="<--",
        callback_data="XR-2")
    )
    await callback.message.edit_text("""Вы выбираете планету XR-2.""", reply_markup=builder.as_markup())

async def planet_xr_3_ok(callback: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Старт!",
        callback_data="XR-3-OK-MAIN")
    )
    builder.add(types.InlineKeyboardButton(
        text="<-- Назад",
        callback_data="XR-3")
    )
    await callback.message.edit_text("""Вы выбираете планету XR-3.""", reply_markup=builder.as_markup())

async def get_profile_menu(callback: types.CallbackQuery):
      pass

async def update_tokens_value():
    pass


@dp.callback_query(F.data == ("start_main"))
async def send_random_value(callback: types.CallbackQuery):
	await planet_xr_1(callback)

@dp.callback_query(F.data == ("XR-1"))
async def send_random_value(callback: types.CallbackQuery):
	await planet_xr_1(callback)
     
@dp.callback_query(F.data == ("XR-2"))
async def send_random_value(callback: types.CallbackQuery):
	await planet_xr_2(callback)

@dp.callback_query(F.data == ("XR-3"))
async def send_random_value(callback: types.CallbackQuery):
	await planet_xr_3(callback)


@dp.callback_query(F.data == ("XR-1-OK"))
async def send_random_value(callback: types.CallbackQuery):
	await planet_xr_1_ok(callback)
     
@dp.callback_query(F.data == ("XR-2-OK"))
async def send_random_value(callback: types.CallbackQuery):
	await planet_xr_2_ok(callback)

@dp.callback_query(F.data == ("XR-3-OK"))
async def send_random_value(callback: types.CallbackQuery):
	await planet_xr_3_ok(callback)
	

@dp.callback_query(F.data == ("XR-1-OK-MAIN"))
async def send_random_value(callback: types.CallbackQuery):
    print(callback.message)
    await main_start(callback)
    
@dp.callback_query(F.data == ("XR-2-OK-MAIN"))
async def send_random_value(callback: types.CallbackQuery):
	await planet_xr_2_ok(callback)

@dp.callback_query(F.data == ("XR-3-OK-MAIN"))
async def send_random_value(callback: types.CallbackQuery):
	await planet_xr_3_ok(callback)

@dp.callback_query(F.data == ("Main-Start"))
async def send_random_value(callback: types.CallbackQuery):
	await main_menu(callback)
	
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

"""
Экономика проекта
XR-1
Старт - получение активного майнера (+1k/hour)
Хранилище - 4K/5K/6K/8K/12K/15K/30K
Сбор каждые 4 часа, но не менее 3.
Возможно улучшить хранилище и майнер. Майнером можно купить несколько, но с уловием, что нет перегрзуке по питанию.  

Добывающие установки. Территория вокруг нужно разведать - 100K Токенов. (+30K каждые 100км). Требуют постройки доп линии питания.
Добыча ресурсов, возможность продажи их на межпланетраном рынке.


Группы. Закрытые/открытые. Таблица лидеров. 
Основные моменты - рынок, инвентарь, улучшения, друзья(группа, таблица лидеров), профиль, энергия"""

"""
Профиль

Имя игрока: 
ID игрока: 
Количество рефералов
Бонус за реферала
Группа
Лига

Планета
Активных майнеров
Активное добывающее оборудования

Майнеры 
1 уровень +1000 OXI/hour
2 уровень + 3500
3 уровень + 8000
4 уровень + 15000
5 уровень + 30000

Лига 
дроны добывапющие  oxi
premium дроны

"""