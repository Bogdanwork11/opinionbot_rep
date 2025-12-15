

import aiogram
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import StateFilter
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from urllib.parse import quote_plus
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.types import (
    CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message, InputMediaPhoto,
    InlineQuery, InlineQueryResultArticle, InputTextMessageContent, BufferedInputFile
)
from aiogram import Router
from telegram import Update
from states.status import FSMTest, router as states_router
from handlers.callback_index import answer_list
from PIL import Image, ImageDraw, ImageFont
from db.db import add_users
from db.db import add_results
from db.db import check_relation
from handlers.admins import router as admins_router
from urllib.parse import quote_plus



    


def progress_bar(now_poz, total, answered):
    full = "🟩"   # отвеченные
    not_ans = "⬜"  # не отвеченные
    black = "◼️"  # текущий вопрос

    bar = ""
    for i in range(1, total + 1):
        if i <= answered:
            bar += full
        elif i == now_poz:
            bar += black
        else:
            bar += not_ans
    return bar


   

#импорт состояний
dp = Dispatcher()
dp.include_router(states_router)



bot_token = "8220005101:AAFxqWdhCoevrbHtW1gAn396YioLKVP0sWM"
BOT_USERNAME = "opiniondevelopment_bot"



bot = Bot(bot_token)

router = Router()

from urllib.parse import quote_plus

def user_link(user_id: int) -> tuple[str, str]:
    test_link = f"https://t.me/{BOT_USERNAME}?start=classic_{user_id}"
    share_url = f"https://t.me/share/url?url={quote_plus(test_link)}"
    return test_link, share_url


#--- Обработка deeplink ---

@router.message(F.text.startswith("/start classic_"))
async def process_start_with_id(message: types.Message, state: FSMContext):
    user2_id = message.from_user.id
    
    #получение идшника пользователя
    link_data = message.text.split("classic_")
    if len(link_data) < 2 or not link_data[1].isdigit():
        await message.answer("увы ссылка не правильна")
        return

    first_user_id = int(link_data[1])
    first_chat_id = first_user_id

    await state.update_data(first_user_id=first_user_id)
    await state.update_data(first_chat_id=first_chat_id)
    await state.update_data(user2_id=user2_id)

    # Генерируем ссылку владельца
    test_link, share_url = user_link(first_user_id)

    
    if user2_id == first_user_id:

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🤖 ПОДЕЛИТЬСЯ", url=share_url)],
            [InlineKeyboardButton(text="📊 Статистика", callback_data="view_result")],
            [InlineKeyboardButton(text="👀 Посмотреть мнения", callback_data="opinion")]
        ])

        await message.answer(
            "<b>👋 Привет, тут ты можешь узнать мнение о себе от твоих друзей и знакомых!</b>\n\n"
            "<b>⭐️ Твоя личная ссылка 👇:</b>\n\n"
            f"🔗 {test_link}\n\n"
            "<i>Опубликуй её, чтобы узнать, что о тебе думают 🤔</i>",
            parse_mode="HTML",
            reply_markup=keyboard
        )
        return

    #проверка взаимности
    relation = await check_relation(first_user_id, user2_id)

    if relation:
        # Получаем ссылки
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🤖 ПОДЕЛИТЬСЯ", url=share_url)],
            [InlineKeyboardButton(text="📊 Статистика", callback_data="view_result")],
            [InlineKeyboardButton(text="👀 Посмотреть мнения", callback_data="opinion")]
        ])

        try:
            owner_chat = await bot.get_chat(first_user_id)
            owner_name = owner_chat.first_name
        except:
            owner_name = "пользователя"

        await message.answer(
            f"<b>😌 Ты можешь оставить своё мнение для {owner_name} только один раз.</b>",
            parse_mode="HTML",
            reply_markup=keyboard
        )
        return

    #логика прописи если нету взаимности
    await start_second_user_test(message, state, user2_id)

    # Добавляем владельца ссылки в USERS
    first_chat = await bot.get_chat(first_user_id)
    first_user_name = first_chat.first_name
    #(БД внос данных в таблицу)
    await add_users(first_user_id, first_user_name)

   
    #Рабочий код старого кода отсюда продолжение   
# #Первое сообщение
@router.message(Command("start"))
async def cmd_start(message:Message, state: FSMContext):
    user_id = message.from_user.id
    print(f"первый пользователь {user_id}")
    
    
    #await state.update_data(chat_id=message.chat.id)
    # chat_id = message.chat.id 
    # await state.update_data(chat_id=message.chat.id)
    #await state.update_data(second_user_id = message.from_user.id)
    
    test_link, share_url = user_link(user_id)

    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text = "🤖 ПОДЕЛИТЬСЯ", url = share_url)],
        [InlineKeyboardButton(text = "📊 Статистика", callback_data = "view_result")],
        [InlineKeyboardButton(text = "👀 Посмотреть мнения", callback_data = "opinion")]
    ])
    
    await message.answer(
        "<b>👋 Привет, тут ты можешь узнать мнение о себе от твоих друзей и знакомых!</b>\n\n"
        "<b>⭐️ Твоя личная ссылка 👇:</b>\n\n"
        f"🔗 {test_link}\n\n"
        "<i>Опубликуй её, чтобы узнать, что о тебе думают 🤔</i>",
        parse_mode="HTML",
        reply_markup=keyboard
    )
    

        
async def start_second_user_test(message: types.Message, state: FSMContext, second_user_id: int):
    # data = await state.get_data()
    # print(data)
    
    #Эта строчка снизу сделанна для того чтобы внести в date информацию о втором пользователе, это помогает выносить id пользователя вне функций
    data = await state.update_data(second_user_id = second_user_id) #(second_user_id = message.from_user.id)
    print(f"строка начальная 151 {data}")
    #последующие пять строчек скрипта и особенно mention, исользуется для показа второму пользователю username 1 пользователя
    first_user_id = data.get("first_user_id")
    
    first_chat = await bot.get_chat(first_user_id)
    #first_user_name = first_chat.first_name
    first_user_name = data.get("first_user_name")
    
    if first_user_name == None:
        first_user_name = first_chat.first_name
    
    
    #Интернет связка-код для получения first_name
    mention = f'<a href="tg://user?id={first_user_id}">{first_user_name}</a>' #first_chat.first_name
    text = f"<b>⭐️Кто для тебя {mention}</b>?"
    #print(mention) 
    # инициализация пустого списка ответов(ЗДЕСЬ ДОБАВИЛ ПРОГРЕССБАР, #остановка здесь докончить)
    await state.update_data(answers=[])
    progress = progress_bar(now_poz=1, total=7, answered=0)
    text = f"{progress} 1/7\n\n{text}"

    
    
    buttons_question_1 = [
        InlineKeyboardButton(text = "✊ ЛД", callback_data="q:0:0"),
        InlineKeyboardButton(text = "💅 ЛП", callback_data="q:0:1"),
        InlineKeyboardButton(text = "❤️ Пара", callback_data="q:0:2"),
        InlineKeyboardButton(text = "🖕 Враг", callback_data="q:0:3"),
        InlineKeyboardButton(text = "🚫 Никто", callback_data="q:0:4"),
        InlineKeyboardButton(text = "👀 ХЗ", callback_data="q:0:5"),
        InlineKeyboardButton(text = "🙃 Просто друг", callback_data="q:0:6"),
        InlineKeyboardButton(text = "✋ Знакомый", callback_data="q:0:7"),
        InlineKeyboardButton(text = "🕶️ Сестра/Брат", callback_data="q:0:8")
    ]
    
    first_step = buttons_question_1[:3]
    second_step = buttons_question_1[3:6]
    third_step = buttons_question_1[6:8]
    fourth_step = buttons_question_1[8:]
    
    keyboard_question_1 = types.InlineKeyboardMarkup(inline_keyboard=[
        first_step,
        second_step,
        third_step,
        fourth_step
    ])
    
    # сохранить message_id для следующих вопросов
    sent = await message.answer(text, parse_mode = "HTML", reply_markup = keyboard_question_1)
    
    # ставим состояние
    await state.update_data(message_id=sent.message_id)
    await state.set_state(FSMTest.s_question_1)
   
    
    data = await state.get_data()
    await state.update_data(second_user_id=second_user_id)

    # Удаляем ошибочный вызов get_data("user2_id")

    # Получаем имя второго пользователя
    chat2 = await bot.get_chat(second_user_id)
    second_user_name = chat2.first_name

    await state.update_data(second_user_name=second_user_name)

    us2 = f'<a href="tg://user?id={second_user_id}">{second_user_name}</a>'
    print("Второй пользователь: строка 220", second_user_name)

    a1 = await state.get_data()
    print(f"Строка 211 {a1}")
    #(БД USERS) Добавляем в таблицу users
    await add_users(second_user_id, second_user_name)

    

#Обработка ответа на первый вопрос и переход ко второму
@router.callback_query(StateFilter(FSMTest.s_question_1, FSMTest.s_question_1), F.data.startswith("q:0"))
async def process_answer_1(callback: CallbackQuery, state: FSMContext):
    answer_value = callback.data.split(":")[2]
    try:
        answer = int(answer_value)
    except ValueError:
        print(f"Некорректный формат ответа для вопроса 1: {callback.data}") 
        await callback.answer("Произошла ошибка. Попробуйте еще раз")
        return 
        
    data = await state.get_data()
    message_id = callback.message.message_id
    answers = data.get("answers", []) 
    answers.append(answer)
    await state.update_data(s_question_1 = answer, answers = answers) 
    print(answers)
    #ansered = len(answers) #дает понять на каком на каком вопросе мы сейчас
    #print(message_id)
    
        
    
    #####-----Второй вопрос-----#####
    data = await state.get_data()
    #последующие пять строчек скрипта и особенно mention, исользуется для показа второму пользователю username 1 пользователя
    first_user_id = data.get("first_user_id")
    
    first_chat = await bot.get_chat(first_user_id)
    first_user_name = first_chat.first_name
    
    #print(data)
    answers = data.get("answers", [])
    #answered = len(answers)
    #добавление проверки и сохранение анонима, добавил 17:36
    first_user_id = data.get("first_user_id")
    
    first_chat = await bot.get_chat(first_user_id)
    #first_user_name = first_chat.first_name
    first_user_name = data.get("first_user_name")
    
    if first_user_name == None:
        first_user_name = first_chat.first_name

    progress = progress_bar(now_poz=2, total=7, answered=1)
    text = f"{progress} 2/7\n\n<b>🎀Что тебе нравится в {first_user_name} больше всего</b>"

    
    buttons_question_2 = [
        InlineKeyboardButton(text = "🤣 Юмор", callback_data = "q:1:0"),
        InlineKeyboardButton(text = "🎤 Голос", callback_data = "q:1:1"),
        InlineKeyboardButton(text = "✨ Характер", callback_data = "q:1:2"),
        InlineKeyboardButton(text = "🍑 Фигура", callback_data = "q:1:3"),
        InlineKeyboardButton(text = "😍 Внешность", callback_data = "q:1:4"),
        InlineKeyboardButton(text = "❤️‍🔥 Всё", callback_data = "q:1:5"),
        InlineKeyboardButton(text = "🖤 Ничего", callback_data = "q:1:6")
    ]
    
    first_step = buttons_question_2[:2]
    second_step = buttons_question_2[2:4]
    third_step = buttons_question_2[4:6]
    fourth_step = buttons_question_2[6:]
    
    keyboard_question_2 = types.InlineKeyboardMarkup(inline_keyboard = [
        first_step,
        second_step, 
        third_step,  
        fourth_step 
    ])
    
    # сохранить message_id для следующих вопросов
    #sent_message = await callback.message(text, parse_mode = "HTML", reply_markup = keyboard_question_2)
    
    
    await bot.edit_message_text( 
        chat_id=callback.message.chat.id, 
        message_id=message_id, 
        text=text, 
        reply_markup=keyboard_question_2, 
        parse_mode="HTML" )
    
    await state.set_state(FSMTest.s_question_2)
    print("Дошло до обработчика переходов")
    
    #await state.update_data(message_id=sent_message.message_id)
    #await callback.answer()
    
    
#Обработка ответа на второй вопрос и переход к третьему
@router.callback_query(StateFilter(FSMTest.s_question_2, FSMTest.s_question_2), F.data.startswith("q:1"))
async def process_answer_2(callback: CallbackQuery, state: FSMContext):
    answer_value = callback.data.split(":")[2]
    try:
        answer = int(answer_value)
    except ValueError:
        print(f"Некорректный формат ответа для вопроса 2: {callback.data}") 
        await callback.answer("Произошла ошибка. Попробуйте еще раз")
        return 
        
    data = await state.get_data()
    message_id = callback.message.message_id
    answers = data.get("answers", []) 
    answers.append(answer)
    await state.update_data(s_question_2 = answer, answers = answers) 
    print(answers)
    #print(message_id)
    
#####-----Третий вопрос-----#####
    data = await state.get_data()    #Метод data = await state.get_data() используется для получения данных, сохраненных в контексте состояния (FSM) пользователя в асинхронных приложениях, таких как боты на Python

    first_user_id = data.get("first_user_id")
    first_chat = await bot.get_chat(first_user_id)
    first_user_name = first_chat.first_name

    answers = data.get("answers", [])
    #answered = len(answers)
    #добавление проверки и сохранение анонима, добавил 17:47
    first_user_id = data.get("first_user_id")
    
    first_chat = await bot.get_chat(first_user_id)
    #first_user_name = first_chat.first_name
    first_user_name = data.get("first_user_name")
    
    if first_user_name == None:
        first_user_name = first_chat.first_name

    progress = progress_bar(now_poz=3, total=7, answered=2)
    text = f"{progress} 3/7\n\n<b>😽 Что ты хочешь сделать с {first_user_name}?</b>"


    buttons_question_3 = [
        InlineKeyboardButton(text = "🫦 Поцеловать", callback_data = "q:2:0"),
        InlineKeyboardButton(text = "😏 Замутить", callback_data = "q:2:1"),
        InlineKeyboardButton(text = "🫂 Обнять", callback_data = "q:2:2"),
        InlineKeyboardButton(text = "🤬 Послать", callback_data = "q:2:3"),
        InlineKeyboardButton(text = "💞 Полюбить", callback_data = "q:2:4"),
        InlineKeyboardButton(text = "🍿 Сходить в кино", callback_data = "q:2:5"),
        InlineKeyboardButton(text = "🍻Побухать", callback_data = "q:2:6"),
        InlineKeyboardButton(text = "👊Побить", callback_data = "q:2:7")
    ]

    first_step = buttons_question_3[:2]
    second_step = buttons_question_3[2:4]
    third_step = buttons_question_3[4:6]
    fourth_step = buttons_question_3[6:7]
    fifth_step = buttons_question_3[7:8]

    keyboard_question_3 = types.InlineKeyboardMarkup(inline_keyboard = [
        first_step,
        second_step,
        third_step,
        fourth_step,
        fifth_step
    ])

#Теперь изменим предыдущее сообщение на новое
    await bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=message_id,
        text=text,
        reply_markup=keyboard_question_3,
        parse_mode="HTML"
    )

    #Сохраним полученное значение в состояние
    await state.set_state(FSMTest.s_question_3)
    print("Дошло до обработчика переходов 3")

#Обработка ответа на третий вопрос и переход к четвертому
@router.callback_query(StateFilter(FSMTest.s_question_3, FSMTest.s_question_3), F.data.startswith("q:2"))
async def process_answer_3(callback: CallbackQuery, state:FSMContext):
    answer_value = callback.data.split(":")[2]
    try:
        answer = int(answer_value)
    except ValueError:
        print(f"Некорректный формат ответа для вопроса 3: {callback.data}") 
        await callback.answer("Произошла ошибка. Попробуйте еще раз")
        return 
    
    data = await state.get_data()
    message_id = callback.message.message_id
    answers = data.get("answers", [])
    answers.append(answer)
    await state.update_data(s_question_3 = answer, answers = answers)
    print(answers) 
    
    
#####-----Четвертый вопрос-----#####

    data = await state.get_data() #Метод data = await state.get_data() используется для получения данных, сохраненных в контексте состояния (FSM) пользователя в асинхронных приложениях, таких как боты на Python
#получение для второго пользователя в сообщении username 1 пользователя
    first_user_id = data.get("first_user_id")

    first_chat = await bot.get_chat(first_user_id)
    first_user_name = first_chat.first_name
    
    answers = data.get("answers", [])
    #answered=len(answers)
    #добавление проверки и сохранение анонима, добавил 17:49
    first_user_id = data.get("first_user_id")
    
    first_chat = await bot.get_chat(first_user_id)
    #first_user_name = first_chat.first_name
    first_user_name = data.get("first_user_name")
    
    if first_user_name == None:
        first_user_name = first_chat.first_name
        
    progress = progress_bar(now_poz = 4, total = 7, answered = 3)
    text = f"<b>{progress} 4/7\n\n❓ Как долго вы с {first_user_name} знаете друг друга?</b>"

    buttons_question_4 = [
        InlineKeyboardButton(text = "🗒️ 1 день", callback_data = "q:3:0"),
        InlineKeyboardButton(text = "📆 Неделю", callback_data = "q:3:1"),
        InlineKeyboardButton(text = "💫 Месяц", callback_data = "q:3:2"),
        InlineKeyboardButton(text = "🕰️ Год", callback_data = "q:3:3"),
        InlineKeyboardButton(text = "⌛️ Больше года", callback_data = "q:3:4"),
        InlineKeyboardButton(text = "🕶️ Всю жизнь", callback_data = "q:3:5"),
        InlineKeyboardButton(text = "🤫 Секрет", callback_data = "q:3:6")
    ]

    first_step = buttons_question_4[:2]
    second_step = buttons_question_4[2:4]
    third_step = buttons_question_4[4:6]
    fourth_step = buttons_question_4[7:]
    
    keyboard_question_4 = types.InlineKeyboardMarkup(inline_keyboard = [
        first_step,
        second_step,
        third_step,
        fourth_step
    ])
    
    await bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=message_id,
        text = text,
        reply_markup = keyboard_question_4,
        parse_mode="HTML"
    )
    
    await state.set_state(FSMTest.s_question_4)
    print("Дошло до обработчика перходов 4")
    
@router.callback_query(StateFilter(FSMTest.s_question_4, FSMTest.s_question_4), F.data.startswith("q:3"))
async def process_answer_4(callback: CallbackQuery, state: FSMContext):
    answer_value = callback.data.split(":")[2]
    try:
        answer = int(answer_value)
    except ValueError:
        print(f"Некорректный формат ответа для вопроса 4: {callback.data}") 
        await callback.answer("Произошла ошибка. Попробуйте еще раз")
        return 
    
    data = await state.get_data()
    message_id = callback.message.message_id
    answers = data.get("answers", [])
    answers.append(answer)
    await state.update_data(s_question_4 = answer, answers = answers)
    print(answers)   

#####-----Пятый вопрос-----#####
    data = await state.get_data()
    #Нижние пять строчек используются для сохранения user_name 1 пользователя
    first_user_id = data.get("first_user_id")
    
    first_chat = await bot.get_chat(first_user_id)
    first_user_name = first_chat.first_name 
    
    #добавление проверки и сохранение анонима, добавил 17:49
    first_user_id = data.get("first_user_id")
    
    first_chat = await bot.get_chat(first_user_id)
    #first_user_name = first_chat.first_name
    first_user_name = data.get("first_user_name")
    
    if first_user_name == None:
        first_user_name = first_chat.first_name
    
    progress = progress_bar(now_poz=5, total=7, answered=4)
    text = f"<b>{progress} 5/7\n\n✌️ Какой смайлик больше всего похож на {first_user_name} Или отправь ей свой вариант: </b>"
    
    buttons_question_5 = [
        InlineKeyboardButton(text="🤪", callback_data = "q:4:0"),
        InlineKeyboardButton(text="😮‍💨", callback_data = "q:4:1"),
        InlineKeyboardButton(text="💩", callback_data = "q:4:2"),
        InlineKeyboardButton(text="👶", callback_data = "q:4:3"),
        InlineKeyboardButton(text="👺", callback_data = "q:4:4"),
        InlineKeyboardButton(text="🦧", callback_data = "q:4:5"),
        InlineKeyboardButton(text="💸", callback_data = "q:4:6"),
        InlineKeyboardButton(text="🔞", callback_data = "q:4:7"),
        InlineKeyboardButton(text="🤡", callback_data = "q:4:8")
    ]
    
    first_step = buttons_question_5[:3]
    second_step = buttons_question_5[3:6]
    third_step = buttons_question_5[6:9]
    
    keyboard_question_5 = types.InlineKeyboardMarkup(inline_keyboard = [
        first_step,
        second_step,
        third_step
    ])
    
    # await bot.edit_message_text(
    #     chat_id = callback.message.chat.id,
    #     message_id = message_id,
    #     text = text,
    #     reply_markup = keyboard_question_5,
    #     parse_mode = "HTML"
    # )
    await bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=message_id,
        text=text,
        reply_markup=keyboard_question_5,
        parse_mode="HTML"
    )

    # Переводим в состояние ожидания текстового сообщения
    await state.set_state(FSMTest.waiting_fact)

    
    await state.set_state(FSMTest.s_question_5)
    print("Дошло до обработчика переходов 5")

@router.callback_query(StateFilter(FSMTest.s_question_5), F.data.startswith("q:4"))
async def process_answer_5(callback:CallbackQuery, state:FSMContext):
    answer_value = callback.data.split(":")[2]
    try:
        answer = int(answer_value)
    except ValueError:
        print(f"Некорректный формат ответа для вопроса 5: {callback.data}") 
        await callback.answer("Произошла ошибка. Попробуйте еще раз")
        return 
        
    data = await state.get_data()
    message_id = callback.message.message_id
    answers = data.get("answers", [])
    answers.append(answer)
    await state.update_data(s_question_5 = answer, answers = answers)
    print(answers)
    
    

    
#####-----Шестой вопрос-----#####
    data = await state.get_data()
    #Нижние пять строчек используются для сохранения username 1 пользователя
    first_user_id = data.get("first_user_id")
    first_chat = await bot.get_chat(first_user_id) 
    first_user_name = first_chat.first_name
    
    #добавление проверки и сохранение анонима, добавил 17:50
    first_user_id = data.get("first_user_id")
    
    first_chat = await bot.get_chat(first_user_id)
    #first_user_name = first_chat.first_name
    first_user_name = data.get("first_user_name")
    
    if first_user_name == None:
        first_user_name = first_chat.first_name
    
    progress = progress_bar(now_poz=6, total=7, answered=5)
    text = f"<b>{progress} 6/7 \n\n🤭Напиши любой факт о {first_user_name}...</b>"
    
    buttons_question_6 = [
        InlineKeyboardButton(text="➡️ Пропустить", callback_data = "q:5:0")
    ]
    
    first_step = buttons_question_6[:1]
    
    keyboard_question_6 = types.InlineKeyboardMarkup(inline_keyboard = [
        first_step
    ])
    
    await bot.edit_message_text(
        chat_id = callback.message.chat.id,
        message_id = message_id,
        text = text,
        reply_markup = keyboard_question_6,
        parse_mode = "HTML"
    )
    
    # Бот теперь ждёт текст ИЛИ нажатие "Пропустить"
    # await state.set_state(FSMTest.waiting_fact)
    await state.set_state(FSMTest.s_question_6)
    
    
    # данный ручной код рабочий, но не достаточный, узнать почему и исправить данное недоразумение
    # ПРОПИСЫВАЕМ СОСТОЯНИЕ ОЖИДАНИЯ ОТВЕТА ОТ message пользователя(ответ с кго клавиатуры)
# @router.message(StateFilter(FSMTest.waiting_fact)) #StateFilter(FSMTest.waiting_fact)-данный обработчик не работает на состояние, нужно пробовать другой    
# async def fact(message: types.Message):
#     #await message.answer(message.text)

#     fact_text = message.text
#     data = await state.get_data()
#     answers = data.get("answers", [])
#     answers.append(fact_text)
#     print(answers)
#     print(fact_text)

@router.message(StateFilter(FSMTest.s_question_6))
async def fact(message: Message, state: FSMContext):
    user_id = message.from_user.id
    print(user_id)
    # print(message)
    fact_text = message.text
    if len(fact_text) < 5:
        messageinfo = await message.answer("‼️ Данный секрет слишком короткий. Количество символов не должно быть менее 5.")
        await asyncio.sleep(5)
        await message.delete()
        await messageinfo.delete()
        return
        
    await state.update_data(fact_value = fact_text)   
    await message.delete()
    
    

    #data = await state.get_data()
    # answers = data2.get("answers", [])
    # print(data)
    # answers.append(fact_text)
    answers2 = []
    answers2.append(fact_text)
    print(answers2)
    #await state.update_data(secmes_question_6 = answers2, answers = answers2)
    

    
    #print("Список ответов:", data) #answers
    await question_7(message, bot, state)

@router.callback_query(StateFilter(FSMTest.s_question_6))
async def process_answer_6(callback:CallbackQuery, state: FSMContext):
    
    #----------здесь ищи callback-----------
    # user_id = callback.message.from_user.id
    # print(user_id)
    answer_value = callback.data.split(":")[2]
    try:
        answer = int(answer_value)
    except ValueError:
        print(f"Некорректный формат ответа для вопроса 6: {callback.data}") 
        await callback.answer("Произошла ошибка. Попробуйте еще раз")
        return 
        
    data = await state.get_data()
    message_id = callback.message.message_id
    answers = data.get("answers", [])
    answers.append(answer)
    await state.update_data(fact_value = "Пропущено")
    print(answers)
    await question_7(callback.message, bot, state)

####-----Седьмой вопрос-----#####
async def question_7(event, bot, state):
    data = await state.get_data()

    first_user_id = data.get("first_user_id")
    message_id = data.get("message_id")

    first_chat = await bot.get_chat(first_user_id)
    first_user_name = first_chat.first_name

    progress = progress_bar(now_poz=7, total=7, answered=6)

    text = (
        f"<b>{progress} 7/7\n\n"
        f"🤫 Отправить ответы анонимно?</b>"
    )

    buttons_question_7 = [
        InlineKeyboardButton(text="❌ Нет", callback_data="q:6:0"),
        InlineKeyboardButton(text="✅ Да", callback_data="q:6:1")
    ]
    
    first_step = buttons_question_7[:2]
    
    keyboard_question_7 = types.InlineKeyboardMarkup(inline_keyboard = [
        first_step
    ])

    await bot.edit_message_text(
        chat_id=event.chat.id,
        message_id=message_id,
        text=text,
        reply_markup=keyboard_question_7,
        parse_mode="HTML"
    )
    # Последние четыре строчки обьясняют и помогают вытащить ид пользователя, как раз вот для меня нужноеееее
    
    #print(data)
    
    
    #----------закоментировал 20 37
    # second_user_id = event.from_user.id
    # print("second_user_id in question_7:", second_user_id)

    # await state.update_data(second_user_id=second_user_id)

    
    await state.set_state(FSMTest.s_question_7)
    
@router.callback_query(StateFilter(FSMTest.s_question_7))
async def process_answer_7(callback:CallbackQuery, state: FSMContext):
    answer_value = callback.data.split(":")[2]
    try:
        answer = int(answer_value)
    except ValueError:
        print(f"Некорректный формат ответа для вопроса 7: {callback.data}") 
        await callback.answer("Произошла ошибка. Попробуйте еще раз")
        return 
        
    data = await state.get_data()
    message_id = callback.message.message_id
    answers = data.get("answers", [])
    answers.append(answer)
    await state.update_data(s_question_7 = answer, answers = answers)
    # print(answers)
    #(БД results) Добавляем в таблицу results
    data = await state.get_data()
    print(data)
    from_user_id = data.get("second_user_id") #откого т е кто проходил тест
    print(f"строка 703 принимает{from_user_id}")
    to_user_id = data.get("first_user_id") #кому т е владельцу ссылки
    answers_list = data.get("answers", [])
    sec_message = data.get("fact_value", "Пропущено")
    await add_results(from_user_id, to_user_id, answers_list, sec_message)
    
    print("Сохранено в БД:", from_user_id, to_user_id, answers_list, sec_message)
    
    data = await state.get_data()

    first_user_id = data.get("first_user_id")
    message_id = data.get("message_id")

    first_chat = await bot.get_chat(first_user_id)
    first_user_name = first_chat.first_name
    text = (f"<b>🐣 Вы успешно оставили своё мнение о {first_user_name}👇!</b>")
    
    
    await bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=message_id,
        text = text,
        # reply_markup = keyboard_question_7,
        parse_mode="HTML"
    )
    
    s_question_1 = data.get("s_question_1")
    s_question_2 = data.get("s_question_2")
    s_question_3 = data.get("s_question_3")
    s_question_4 = data.get("s_question_4")
    s_question_5 = data.get("s_question_5")
    fact_value = data.get("fact_value", "Пропущено")

    ans1 = answer_list[1][s_question_1]
    ans2 = answer_list[2][s_question_2]
    ans3 = answer_list[3][s_question_3]
    ans4 = answer_list[4][s_question_4]
    ans5 = answer_list[5][s_question_5]

    # secmes_s_question_6 = data.get("secmes_s_question_6")
    # s_question_6 = data.get("s_question_6")
    fact_value = data.get("fact_value", "Пропущено")
    s_question_7 = data.get("s_question_7")
    fact_value = data.get("fact_value", "Пропущено")
    
    first_chat_id = data.get("first_chat_id")
    
    print("Дело дошло до обработчика отправления автору")
    
    #добавляем конечный ответ
    s_question_7 = data.get("s_question_7")
    answers.append(s_question_7)
    print("добавленный ответ answers", answers)
    
    #Тут начал внедрять pillow
    photo_pil = "E:/Шаблоны Pillow/whitefoto.jpg"#Задал директорию к лежачему файлу на компе
    image = Image.open(photo_pil)
    draw = ImageDraw.Draw(image)
    shrift = ImageFont.truetype('fonts/times.ttf', 32) 
    x, y = 75, 75

    text_to_write = ("Новое мнение...\n\n"
    
    f"-Ты для него/неё:{ans1}\n"
    f"-Нравится в тебе:{ans2}\n"
    f"-Хочет:{ans3}\n"
    f"-Знакомы:{ans4}\n"   
    f"-Факт о тебе: {fact_value}\n\n"
    )
    
    draw.text((x, y), text_to_write, fill='Black', font=shrift)
    # photo_pil.save("E:/Шаблоны Pillow/белое фото.jpg")
    image.save("изображение_с_текстом.jpg")

    
    photo_pil = BufferedInputFile(open('изображение_с_текстом.jpg', "rb").read(), "image.jpg")
    #логика для прописи анонима
    
    data = await state.get_data()
    second_user_id = data.get("second_user_id")
    print(f"строка 783 : {second_user_id}")

    
    answer_7 = data.get("s_question_7")
    
    buttons_question_pil = [
        InlineKeyboardButton(text = "👁️ Раскрыть анонимность", callback_data = f"answer:{second_user_id}:{answer_7}")
    ]
    first_step = buttons_question_pil[:1]
    
    keyboard_question_pil = types.InlineKeyboardMarkup(inline_keyboard = [
        first_step
    ])
    
    
    caption_text = (
    "<b>🐣 Новое мнение</b>\n"
    "<b>👤 Аноним\n\n</b>"
    f"<b>⭐️ Ты для него/неё:{ans1}</b>\n"
    f"<b>🎀 Нравится в тебе:{ans2}</b>\n"
    f"<b>😽 Хочет:{ans3}</b>\n"
    f"<b>❓ Знакомы:{ans4}</b>\n"
    f"<b>✌️Похожий на тебя смайлик:{ans5}</b>\n"   
    f"<b>✉️ Факт о тебе:{fact_value}</b>\n\n"
    "<b>Не забывай делиться классными ответами с друзьями, в историях и в тиктоке!</b>\n\n"
    "@opiniondevelopment_bot")
    
    await bot.send_photo(
        chat_id = first_chat_id,
        photo = photo_pil,
        caption=caption_text,
        reply_markup=keyboard_question_pil,
        parse_mode = "HTML",
        
        )
        
    
    print(answers)
    
    data = await state.get_data()
    #user_id = message.from_user.id
    second_user_id = data.get("second_user_id")
    print(f"строка 825: {second_user_id}")
    test_link_2, share_link_2 = user_link(second_user_id)

    keyboard_link2 = InlineKeyboardMarkup(inline_keyboard = [
        [InlineKeyboardButton(text = "🤖 ПОДЕЛИТЬСЯ", url = share_link_2)],
        [InlineKeyboardButton(text = "📊 Статистика", callback_data = "view_result")],
        [InlineKeyboardButton(text = "👀 Посмотреть мнения", callback_data = "opinion")]    
    ])
    text = f"<b>⭐️ Твоя личная ссылка 👇:</b>\n\n🔗{test_link_2}\n\n<i>Опубликуй её, чтобы узнать, что о тебе думают 🤔</i>"
    await bot.send_message(
        chat_id=callback.message.chat.id,
        text = text,
        parse_mode = "HTML",
        reply_markup=keyboard_link2
    )
    
    await state.set_state(FSMTest.question_pil)
    
# @router.callback_query(StateFilter(FSMTest.question_pil))
# async def process_answer_pil(callback:CallbackQuery, state: FSMContext):
#     answer_value = callback.data.split(":")[2]
#     try:
#         answer = int(answer_value)
#     except ValueError:
#         print(f"Некорректный формат ответа для вопроса c pillow: {callback.data}") 
#         await callback.answer("Произошла ошибка. Попробуйте еще раз")
#         return 
        
#     data = await state.get_data()
#     message_id = callback.message.message_id
#     answers = data.get("answers", [])
#     answers.append(answer)
#     await state.update_data(question_pil = answer, answers = answers)
#     print(answers)
    
    


@router.callback_query(F.data.startswith("answer:"))
async def reveal_identity(callback: CallbackQuery, state: FSMContext):
    
    try:
        _, second_id_str, answer_7 = callback.data.split(":")
        second_id = int(second_id_str)
    except:
        await callback.answer("Ошибка данных.")
        return 

    # Получаем имя второго пользователя
    try:
        chat = await bot.get_chat(second_id)
        name = chat.first_name
    except Exception:
        name = "Пользователь"
    
    #Здесь условие проверки на взаимность к моей кнопке последней оценить в ответ
    first_user_id = callback.message.chat.id
    second_user_id = second_id
    print(f"Проверка взаимности условий 886 первый пользователь:{first_user_id} второй пользователь: {second_user_id}")
    relation = await check_relation(first_user_id, second_user_id)
    
    if relation:
        end_question = None
    else:
        
    
        # Кнопка "Оценить в ответ"
        end_question = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🤩 Оценить в ответ", callback_data=f"back:{second_id}")]
            ]
        )

    
    if answer_7 == "0":
        updated_caption = callback.message.html_text.replace("Аноним", name, 1)

        await bot.edit_message_caption(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            caption=updated_caption,
            reply_markup=end_question,
            parse_mode="HTML"
        )
        await callback.answer()
        return
    

    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=end_question
    )
    await callback.answer()
    
    data1 = await state.get_data()
    print(f"состояние листа 935 {data1}")
    if answer_7 == "1":
        first_user_name = "Аноним"
        await state.update_data(first_user_name="Аноним")
    else: 
        print("Произошла ошибка на строке 937")
    
    
@router.callback_query(F.data.startswith("back"))
async def back(callback: CallbackQuery, state: FSMContext):
    
    try:
        parts = callback.data.split(":")
       
        if len(parts) >= 2 and parts[1].isdigit():
            first_user_id = int(parts[1])
        else:
            first_user_id = None
    except Exception:
        first_user_id = None

    
    if not first_user_id:
        data = await state.get_data()
        first_user_id = data.get("first_user_id")

    if not first_user_id:
        await callback.answer("Не передан ID пользователя для оценки.")
        return

   
    new_second_user_id = callback.from_user.id
    print(f"строка 958 : {new_second_user_id}")

 
    await state.update_data(first_user_id=first_user_id)
    await state.update_data(first_chat_id=first_user_id)


    dats = await state.update_data(second_user_id=new_second_user_id)
    print(f"строка 966 принимает : {new_second_user_id}")

    print("back handler: first_user_id:", first_user_id, "new_second_user_id:", new_second_user_id)
    
    
   
    await start_second_user_test(callback.message, state, callback.from_user.id)
    await callback.answer()

   
    
    
    

    
    
