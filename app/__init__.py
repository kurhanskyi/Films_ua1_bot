from os import getenv

from aiogram import Router, Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.markdown import hbold
from dotenv import load_dotenv

from app.routes.film import film_router

load_dotenv()

root_router = Router()
root_router.include_router(film_router)

async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Запустити бота"),
        BotCommand(command="films", description="Показати список фільмів"),
        BotCommand(command="search", description="Пошук фільму"),
        BotCommand(command="filmcreate", description="Створити новий фільм"),
        BotCommand(command="filmupdate", description="Оновити інформацію про фільм"),
        BotCommand(command="filmdelete", description="Видалити фільм"),
        BotCommand(command="help", description="Показати довідку")
    ]

    await bot.set_my_commands(commands)

@root_router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Вітаю у нашому боті: {hbold(message.from_user.full_name)}!")

@root_router.message(lambda message: message.text.lower() == '/help')
async def command_help_handler(message: Message) -> None:
    help_text = (
        "Доступні команди бота:\n"
        "/start - почати взаємодію з ботом\n"
        "/help - показати меню з командами\n"
        "/films - показати усі фільми\n"
        "/filmcreate - створити фільм\n"
        "/filmdelete - видалити фільм\n"
        "/search назва фільму для пошуку\n"
    )

    await message.answer(help_text)


async def main() -> None:
    TOKEN = getenv("BOT_TOKEN")
    bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode = ParseMode.HTML))

    dp = Dispatcher()
    dp.include_router(root_router)

    await dp.start_polling(bot)










