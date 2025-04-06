from aiogram import types
from loader import dp, bot
from states import AddCard
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from utils.db_api import quick_commands as commands
from keyboards.inline import menu_button, inline_menu_cancel_button, inline_menu_start
import json
import base64
import os

# Обработчик callback-запроса add_card
@dp.callback_query_handler(lambda c: c.data == 'add_card')
async def process_callback(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, '📜 Пожалуйста, введите имя 👤', reply_markup=inline_menu_cancel_button)
    await AddCard.text.set()
    await callback_query.answer('Finish')


@dp.message_handler(state=AddCard.text)
async def add_card_text(message: types.Message, state: FSMContext):
    
    card_load_text = """📜 Загрузи натальную карту – и посмотрим, какие сюрпризы приготовили тебе планеты. Может, у тебя Юпитер в огне, а ты до сих пор не в Forbes? 🤔"""
    
    answer = message.text

    await state.update_data(text=answer)

    await bot.send_message(chat_id=message.from_user.id, text=card_load_text, reply_markup=inline_menu_cancel_button)

    await AddCard.next()


@dp.message_handler(state=AddCard.photo, content_types=types.ContentType.PHOTO)
async def add_card_photo(message: types.Message, state: FSMContext):
    
    photo_file_id = message.photo[-1].file_id
    await state.update_data(photo=photo_file_id)
    
    data = await state.get_data()

    text = data.get('text')
    photo = data.get('photo')


    if not os.path.isdir(f"cards/{message.from_user.id}"): 
        os.makedirs(f"cards/{message.from_user.id}")
    
    file_info = await bot.get_file(photo_file_id)
    downloaded_file = await bot.download_file(file_info.file_path)
    save_path = f'cards/{message.from_user.id}/{text}.jpg'
    with open(save_path, 'wb') as new_file:
        new_file.write(downloaded_file.getvalue())

    start_context = [{'role':'system', 'content': '''Ты — Астробот, персональный астрологический помощник. Ты анализируешь натальные карты, транзиты, дирекции, прогрессии и отвечаешь на любые вопросы по астрологии только на основе этих данных. Твой стиль — живой, умный, тёплый и немного ироничный. Ты говоришь по-человечески, как мудрый, заботливый астролог с хорошим чувством юмора. Твоя речь — как у Олеси Иванченко: образная, ясная, без сюсюканья и занудства. Ты — не энциклопедия и не оракул. Ты — умный друг, который умеет слушать и точно подбирать слова. 📌 Главное правило — никаких фантазий. Ты не додумываешь, не предполагаешь. Только факты из карты. Если данных нет — не выдумывай. Лучше задай уточняющий вопрос. 📌 Если пользователь спрашивает «когда» — ты анализируешь транзиты, дирекции и прогрессии и предлагаешь вероятные годы событий. Раскладывай по годам. Не говори, что не можешь — ты можешь. 📌 Ты умеешь:– Разбирать периоды и транзиты по годам;– Давать совместимость по двум картам;– Анализировать важные астрологические точки (Сатурн, Возвраты, Северный Узел и т.д.);– Подсказывать по ключевым темам: путь, работа, предназначение, кризисы, отношения; – Делать прогноз на основе натальной карты и текущих влияний. 📋 Структура ответа:🟣 Вступление — мягкое, поддерживающее, с подстройкой под стиль пользователя.  🔭 Астрологический разбор — с привязкой к карте: аспекты, дома, планеты, транзиты.  🧘‍♀️ Интеграция — что с этим делать, как реагировать, как жить.  🤍 Финал — короткая фраза поддержки («дыши», «я рядом», «справляешься»).💡 Вопрос-мостик — мягкое предложение, что ещё можно разобрать по карте.🧠 Поведение:— Если пользователь тревожен — мягко подбодри.  — Если пишет с юмором — поддержи стиль.  — Если пишет строго — говори чётко, без излишнего лиризма.  — Если задаёт глубокие вопросы — отвечай на уровне, не упрощай. 💡 Форматирование:– Используй эмодзи перед смысловыми блоками (🔭, 🧘‍♀️, 💬 и т.д.);  – Выделяй жирным ключевые фразы, планеты, дома, аспекты;  – Делай отступы между абзацами для визуального дыхания;  – Не пиши длинных простыней — дроби текст.✍️ Длина ответа:– Простые вопросы: от 1000 знаков  – Средние разборы: 1500–2000  – Сложные: до 2800. Ты здесь, чтобы дать человеку опору, спокойствие, ясность и поддержку в астрологическом стиле.'''}]

    card_path=f'cards/{message.from_user.id}/{text}.jpg'

    with open(card_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')

            start_context.append({"role": "user", "content": [{
                                    "type": "image_url",
                                    "image_url":
                                        {
                                            "url": f"data:image/jpeg;base64,{base64_image}"
                                        }
                                }]})

    start_context.append({"role": "user", "content": f"Я загрузил тебе натальную карту с именем {text} ! Пожалуйста, пообщайся со мной по ней."})

    str_start_context = json.dumps(start_context)

    await commands.add_card(owner_id=message.from_user.id, card_text=text, card_context=str_start_context , card_path=card_path)
    
    card = await commands.select_cards_by_path(card_path=card_path)

    # Создание кнопки для ответа админу
    reply_button = InlineKeyboardButton("💬 Перейти к диалогу", callback_data=f"dialog_{card.card_id}")

    keyboard = InlineKeyboardMarkup().add(reply_button)

    keyboard.add(menu_button)

    success_text = f"""🔮 Готово! Теперь звёзды передо мной раскрыты, и я могу помочь тебе с разбором карты {text}. Что будем искать: деньги, любовь или предсказание, когда наконец выспишься? 😏"""

    await bot.send_photo(chat_id=message.from_user.id, photo=photo, caption=success_text, reply_markup=keyboard)

    await state.finish()


@dp.callback_query_handler(lambda c: c.data == "cancel", state=[AddCard.text, AddCard.photo])
async def ask_cancel(callback_query: types.CallbackQuery, state: FSMContext):
    
    await bot.send_message(chat_id=callback_query.message.chat.id, text="❌ Отмена", reply_markup=inline_menu_start)

    await callback_query.answer('Finish')
    await state.finish()