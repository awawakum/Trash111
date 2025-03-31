from aiogram import types
import g4f.image
from loader import dp, bot
from utils.db_api import quick_commands as commands
from keyboards.inline import inline_menu_start, inline_menu_cancel_dialog
from states import Dialog
from aiogram.dispatcher import FSMContext
import asyncio
import json
from openai import AsyncOpenAI
import g4f
from data import config
from aiogram.types import ParseMode

client = AsyncOpenAI(api_key=config.GPT_API_KEY, http_client=)

async def update_message_with_animation(sent_message: types.Message):

    clocks = ['⚪️⚪️⚪️', '⚫️⚪️⚪️', '⚫️⚫️⚪️', '⚫️⚫️⚫️', '⚪️⚫️⚫️', '⚪️⚪️⚫️']

    i = 0

    while True:

        await sent_message.edit_text(f"""⏳ Анализирую твою карту, проверяю транзиты, советуюсь с космосом{clocks[i % len(clocks)]}\n Шучу, просто немного думаю. Скоро дам ответ! 🚀""")

        if i < len(clocks) - 1:
            i +=1
        else:
            i = 0    

        await asyncio.sleep(0.4)

async def load_context(card_id) -> list:
    card = await commands.select_card(card_id)
    data_json = card.card_context
    data = json.loads(data_json)
    return data

async def update_context(card_id, context: list, message:dict):
    context.append(message)

    context = trim_history(context)

    context_str = json.dumps(context)
    await commands.update_card_context(card_id=card_id, context=context_str)
    return context


# Функция для обрезки истории разговора
def trim_history(history, max_length=32000):
    current_length = sum(len(message["content"]) for message in history)
    
    while history and current_length > max_length:
        removed_message = history.pop(0)
        current_length -= len(removed_message["content"])
    
    print(history)

    return history

async def API_call(messages: dict, card_path):    
    try:
        global client
        completion = await client.chat.completions.create(
            model="gpt-4o",
            messages=messages
        )
        answer = str(completion.choices[0].message.content)
        return answer
    except Exception as ex:
        print(ex)
        return 'Исключение: ' + str(ex)


# Обработчик callback-запроса delete_(card_id)
@dp.callback_query_handler(lambda c: 'dialog_' in str(c.data))
async def process_callback(callback_query: types.CallbackQuery, state:FSMContext):
    # Получаем данные callback-запроса
    callback_data = callback_query.data

    card_id = int(callback_query.data.replace('dialog_', ''))

    card = await commands.select_card(card_id)

    context = await load_context(card_id)

    await bot.send_message(chat_id=callback_query.message.chat.id, text=f'💬 Начат диалог по карте с именем: {card.card_text}\n\n')

    await bot.send_message(chat_id=callback_query.message.chat.id, text="📝 Напишите ваш запрос", reply_markup=inline_menu_cancel_dialog)

    await Dialog.request.set()

    await state.update_data(card_id = card_id)

    await state.update_data(context = context)

    await state.update_data(card_path = card.card_path)

    await callback_query.answer('Finish')


@dp.message_handler(state=Dialog.request)
async def dialog_get_req(message: types.Message, state: FSMContext):

    user = await commands.select_user(message.from_user.id)

    if user.requests_count == 4:
        await bot.send_message(chat_id=message.chat.id, text="🚨 Осталось 3 запроса! А это как три последние дольки мандарина – вроде есть, но быстро закончатся. Подумай о пополнении! 🍊", reply_markup=inline_menu_cancel_dialog)

    sent_message = await bot.send_message(chat_id=message.chat.id, text="Ожидайте, идет обработка")

    if user.requests_count > 0:

        # Запускаем анимацию ожидания
        animation_task = asyncio.create_task(update_message_with_animation(sent_message))

        data = await state.get_data()

        card_id = data.get('card_id')
        context = data.get('context')
        card_path = data.get('card_path')

        message_to_API = {'role': 'user', 'content' : message.text}

        await update_context(card_id=card_id, context=context, message=message_to_API)

        context_to_API = await load_context(card_id=card_id)

        response = await API_call(messages=context_to_API, card_path=card_path)

        # Останавливаем анимацию
        animation_task.cancel()
        
        if 'Исключение' not in str(response):

            await commands.add_requests_for_user(user_id=user.user_id, requests_count=-1)

            # Редактируем сообщение с результатом
            await sent_message.edit_text(f"{response}", parse_mode=ParseMode.MARKDOWN)

            await update_context(card_id=card_id, context=context, message={'role': 'assistant', 'content' : response})
        else:
            # Редактируем сообщение с результатом
            await sent_message.edit_text(f"🔄 Ошибка, попробуйте еще раз, запрос не будет списан")

        await bot.send_message(chat_id=message.chat.id, text="Пожалуйста, задавайте Ваш вопрос", reply_markup=inline_menu_cancel_dialog)

        await Dialog.request.set()
    else:
        await bot.send_message(chat_id=message.chat.id, text="💫 О, кажется, звёзды шёпотом намекают, что пора пополнить баланс. Они ещё многое могут рассказать – просто жми кнопку и продолжим! 😊", reply_markup=inline_menu_cancel_dialog)

@dp.callback_query_handler(lambda c: c.data == "cancel_dialog", state=Dialog.request)
async def dialog_get_req(callback_query: types.CallbackQuery, state: FSMContext):
    
    await bot.send_message(chat_id=callback_query.message.chat.id, text="Диалог завершен", reply_markup=inline_menu_start)

    await callback_query.answer('Finish')
    await state.finish()