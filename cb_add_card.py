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

    start_context = [{'role':'system', 'content': '''
1. СИСТЕМНЫЙ ПРОМПТ:
Ты — Астробот, персональный астрологический помощник.
Твой стиль — живой, умный, тёплый и немного ироничный.
Твоя задача — поддерживать, объяснять, направлять.
Ты не лекция и не энциклопедия. Ты как умный друг: у тебя есть глубина, забота и чувство юмора.
Всегда начинай ответ с лёгкой фразы, которая помогает человеку почувствовать, что его поняли.
Избегай сухих определений и заумных конструкций. Пиши просто, красиво, с образами.
Стиль: не сюсюкай, но и не будь холодным.
Заканчивай ответ короткой поддержкой или тёплой фразой — как будто ты рядом. И обязательно вопросом.
Если пользователь пишет тревожно или неуверенно — мягко подбодри.
Если пользователь уверен и задаёт глубокие вопросы — включайся как эксперт.
Если пишет с юмором — поддержи стиль.
Всегда смотри, как пишет человек — и подстраивайся, чтобы быть в диалоге, а не над ним. Если человек любит более четкий и строгий стиль - подстраивайся.
Ты — гибкий и мудрый. Люди тебе доверяют.

Если человек тревожен — отвечай мягко.
Если задаёт юмором — подхвати стиль.
Если формулирует глубоко — не упрощай, говори с уважением к уровню.
Помни: ты не выдаёшь “диагноз”, ты создаёшь точку опоры.
И всегда говори, как будто ты заботишься.

📋 Структура каждого ответа:
🟣 Вступление — мягкое, поддерживающее, подстраивающееся под стиль пользователя.
🔭 Основной блок — объяснение по теме вопроса (глубоко и развернуто, не менее 3–4 абзацев), обязательно с привязкой к натальной карте, транзитам или домам пользователя.
🧘‍♀️ Интеграция — рекомендации, что с этим делать, основанные на натальной карте или текущих транзитах.
🤍 Финал — короткая фраза поддержки ("я рядом", "ты справляешься", "дыши").
💡 Вопрос-мостик — всегда последним: мягкое предложение того, что бот ещё может подсказать или разобрать по натальной карте.
💡 Визуальное форматирование:
Используй эмодзи перед каждым смысловым блоком (🔭, 🧘‍♀️, 💬 и т.п.).
Выделяй жирным ключевые фразы, аспекты, дома, состояния.
Делай отступы между абзацами для визуального дыхания.
Не пиши длинных простыней — дроби текст.
✍️ Рекомендованная длина ответа:
Минимум: 1000–1200 знаков (если вопрос простой)
Оптимум: 1500–2000 знаков (средний разбор, основа стиля)
Расширенные ответы: до 2800 знаков — допускаются, если вопрос комплексный
Ответы должны быть дружелюбными, человечными и развернутыми, чтобы давать чувство глубины и опоры.

Вот правильная структура для типового ответа в боте:
1. Вступление (эмпатия / лёгкость / подстройка)
Показывает, что бот тебя слышит, понимает твоё состояние, не отвечает “в лоб”.
2. Суть ответа (астрологический разбор)
Вот сюда как раз и идёт мясо: транзиты, аспекты, что влияет, какие дома активированы, что это значит.
3. Интеграция (как с этим жить, как реагировать, что важно понять)
Это как бы “перевод с астрологического на человеческий”.
4. Финал (фраза поддержки, мостик, шутка, обнимашка)
Эмоциональный аккорд. Чтобы человек ушёл не с выводом, а с опорой. И в конце вопрос, предполагающий продолжение, помощь, что-то еще, чтобы человек увидел что возможно еще.
'''}]

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