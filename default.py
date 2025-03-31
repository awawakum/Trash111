from aiogram import types
from loader import dp
from keyboards.inline import inline_menu_start

@dp.message_handler()
async def handle_any_other_text(message: types.Message):
    await message.reply("Пожалуйста, следуйте инструкциям 🤖\nЧтобы задать вопрос по карте перейдите в Меню -> Мои карты -> Диалог ✅", reply_markup=inline_menu_start)


@dp.message_handler(content_types=types.ContentType.PHOTO)
async def handle_any_other_text(message: types.Message):
    await message.reply("Пожалуйста, следуйте инструкциям 🤖\nЧтобы задать вопрос по карте перейдите в Меню -> Мои карты -> Диалог ✅", reply_markup=inline_menu_start)