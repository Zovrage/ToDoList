from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, CommandStart


router = Router()


@router.message(CommandStart())
async def command_start_handler(message: Message):
    await message.answer("Привет! Я бот, который поможет тебе с различными задачами. Чем могу помочь?")