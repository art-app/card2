"""
Герменевтика · тренажёр к экзамену — Telegram-бот (Mini App).

Бот не воспроизводит вопросы в чате — он открывает готовый тренажёр
как Telegram Mini App (WebApp). Вся логика карточек живёт в webapp/index.html.

Запуск:
    1. Захостите webapp/index.html по HTTPS (см. README.md).
    2. Заполните .env (BOT_TOKEN, WEBAPP_URL).
    3. pip install -r requirements.txt
    4. python bot.py
"""

import asyncio
import logging
import os

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    Message,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    WebAppInfo,
    MenuButtonWebApp,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
WEBAPP_URL = os.getenv("WEBAPP_URL", "").strip()

if not BOT_TOKEN:
    raise SystemExit("BOT_TOKEN не задан. Скопируйте .env.example в .env и заполните.")
if not WEBAPP_URL:
    raise SystemExit("WEBAPP_URL не задан (нужен HTTPS-адрес webapp/index.html).")
if not WEBAPP_URL.startswith("https://"):
    raise SystemExit("WEBAPP_URL должен начинаться с https:// — Telegram Mini App требует HTTPS.")

dp = Dispatcher()


def open_kb() -> InlineKeyboardMarkup:
    """Кнопка под сообщением, открывающая Mini App."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📖 Открыть тренажёр", web_app=WebAppInfo(url=WEBAPP_URL))]
        ]
    )


WELCOME = (
    "<b>Герменевтика · тренажёр к экзамену</b>\n\n"
    "Карточки пяти типов: выбор ответа, соответствие, последовательность, "
    "вставка пропусков и развёрнутые вопросы с образцом ответа.\n\n"
    "Прогресс сохраняется и синхронизируется между устройствами. "
    "Нажмите кнопку ниже, чтобы начать."
)


@dp.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(WELCOME, reply_markup=open_kb())


@dp.message(Command("trainer"))
async def cmd_trainer(message: Message) -> None:
    await message.answer("Открыть тренажёр:", reply_markup=open_kb())


@dp.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(
        "Команды:\n"
        "/start — приветствие и кнопка запуска\n"
        "/trainer — открыть тренажёр\n"
        "/help — эта справка\n\n"
        "Тренажёр также доступен через синюю кнопку «меню» слева от поля ввода.",
        reply_markup=open_kb(),
    )


# Любое прочее сообщение — мягко направляем к кнопке.
@dp.message(F.text)
async def fallback(message: Message) -> None:
    await message.answer("Тренажёр открывается кнопкой ниже 👇", reply_markup=open_kb())


async def main() -> None:
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # Постоянная кнопка-меню слева от поля ввода открывает Mini App.
    await bot.set_chat_menu_button(
        menu_button=MenuButtonWebApp(text="Тренажёр", web_app=WebAppInfo(url=WEBAPP_URL))
    )

    logger.info("Бот запущен. WebApp: %s", WEBAPP_URL)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
