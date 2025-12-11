from aiogram import Router, F
from aiogram.types import Message
import db.db as database
from aiogram.types import (
    CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message, InputMediaPhoto,
    InlineQuery, InlineQueryResultArticle, InputTextMessageContent, BufferedInputFile
)
from aiogram.fsm.state import State
from aiogram.fsm.context import FSMContext
from aiogram import Bot

from states.status import FSMsend
from aiogram.filters import StateFilter

router = Router()

admin_id = {7927889042, 273149212, 163482293}

@router.message(F.text == "/admin")
async def admins_panel(message: Message):
    user_id = message.from_user.id
    print(user_id)
    if user_id not in admin_id:
        return await message.answer("Увы доступа у вас нет")
#показ жтвых людей при помощи общего количества пользователей, и таблица к тому же следит кто активен а кто нет      
    live_users = await database.db.fetchval("""
        SELECT COUNT(DISTINCT from_user_id) FROM results
    """
    )
#общее количество пользователей(COUNT(*)-специально для подсчета всех строк в таблице)
    total_users = await database.db.fetchval("""
        SELECT COUNT(*) FROM users
    """
    )
#логика мертвых людей:общее количество - живые пользователи
    dead_users = total_users - live_users
#всего результатов:
    total_results = await database.db.fetchval("""
        SELECT COUNT(*) FROM results
    """
    )
#Всего созданных тестов(только уникальные значения)
    total_tests = await database.db.fetchval("""
        SELECT COUNT(DISTINCT to_user_id) FROM results
    """
    )
#Среднее арифметическое мнений
    avg_check = 0
    if total_tests > 0:
        avg_check = round(total_results / total_tests)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard = [[InlineKeyboardButton(text = "Рассылка", callback_data = "send")]])
    text = (
            "<b>🧑‍💻 Меню администратора</b>\n\n"
            f"<b>👤 Живых пользователей: {live_users}</b>\n"
            f"<b>☠️ Мертвых пользователей: {dead_users}</b>\n"
            f"<b>➮ Всего созданных тестов: {total_tests}</b>\n"
            f"<b>➮ Среднее количество мнений: {avg_check}</b>\n"
            f"<b>➮ Всего результатов: {total_results}</b>\n\n"
            "<b>💥 Ниже вас ожидает кнопка: Рассылка</b>\n"
            "<b>Использовав её вы можете отправить рекламу для всех пользователей бота</b>"
            
        )
    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")
    



# mail_text = State()

@router.callback_query(F.data == "send")
async def send_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "<i>👨‍💻 Напишите сообщение которое желаете разослать для пользователей бота</i>",
        parse_mode="HTML"
    )
    # await state.set_state(mail_text)
    await state.set_state(FSMsend.mail_text)
    


@router.message(StateFilter(FSMsend.mail_text))
async def get_mail_text(message: Message, state: FSMContext):
    text = message.text
    await state.clear()
    bot = message.bot   
    
    
    chat_origin = message.chat.id
    message_orig= message.message_id
    print("полученный текст:", text)

    #сохранение текста
    await state.update_data(get_text=text)

    #получение слхранение текста
    data = await state.get_data()
    get_text = data["get_text"]
    print(f"строка 109{get_text}")
    print(data)
    # await state_finish()

    
    #вывод с бд ид пользователей
    users = await database.db.fetch("SELECT id FROM users")

    #цикл для рассылки каждому пользоателю
    for u in users:
        user_id = u["id"]
        try:
            await bot.copy_message(
                chat_id=user_id,           
                from_chat_id=chat_origin, 
                message_id=message_orig   
                )
        except Exception as e:
            print(f"Не удалось отправить пользователю {user_id}: {e}")

    await message.answer(
        "<b>Ваше сообщение успешно обработано 👨‍💻.</b>\n"
        "<b>Всем пользователям уже доступно ваше сообщение 💬💬💬</b>", 
        parse_mode="HTML")
    
    
