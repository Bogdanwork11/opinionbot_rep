

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup

from db.db import get_results
from db.db import your_opinion
from db.db import check_relation


from handlers.message_origin import user_link
from db.db import get_results2
from handlers.callback_index import answer_list

from aiogram import F
from aiogram.types import (
    CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message, InputMediaPhoto,
    InlineQuery, InlineQueryResultArticle, InputTextMessageContent, BufferedInputFile)


router = Router()

@router.message(Command("stats"))
async def cmd_stats(message: Message):
    user_id = message.from_user.id
    
    total_results = await get_results(user_id)
    total_your_opinion = await your_opinion(user_id)
    if total_results == 0:
        await message.answer("Увы, у вас пока нет мнений...")
        return
    text = ("<b>📊 Твоя статистика:</b>\n\n"
        f"<b>✨Мнений о тебе оставили: {total_results}</b>\n"
        f"<b>💫 Твоих мнений: {total_your_opinion}</b>\n\n"
        f"<i>📲 Отправляй свою ссылку и получай еще больше мнений о тебе от друзей 👥</i>"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard = [
        [InlineKeyboardButton(text="👀 Посмотреть мнения", callback_data="opinion")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data = "stats_back")]
    ])
    
    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")
    
@router.callback_query(F.data == "stats_back")
async def back_handler(callback: CallbackQuery):
    user_id = callback.from_user.id #Для оьязательного получения ид
    test_link, share_url = user_link(user_id) #сбор ссылки с функции messagepy
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🤖 ПОДЕЛИТЬСЯ", url=share_url)],
        [InlineKeyboardButton(text="📊 Статистика", callback_data="view_result")],
        [InlineKeyboardButton(text="👀 Посмотреть мнения", callback_data="opinion")]
    ])
    
    text = (
        "<b>⭐️ Твоя личная ссылка 👇:</b>\n\n"
        f"🔗 {test_link}\n\n"
        "<i>Опубликуй её, чтобы узнать, что о тебе думают 🤔</i>"
        
    )
    
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=keyboard)
    await callback.answer()
    
@router.callback_query(F.data == "view_result")
async def stats_res(callback: CallbackQuery):
    user_id = callback.from_user.id 
    print(user_id)
    
    total_results = await get_results(user_id)
    total_your_opinion = await your_opinion(user_id)
    if total_results == 0:
        await message.answer("Увы, у вас пока нет мнений...")
        return
    text = ("<b>📊 Твоя статистика:</b>\n\n"
        f"<b>✨Мнений о тебе оставили: {total_results}</b>\n"
        f"<b>💫 Твоих мнений: {total_your_opinion}</b>\n\n"
        f"<i>📲 Отправляй свою ссылку и получай еще больше мнений о тебе от друзей 👥</i>"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard = [
        [InlineKeyboardButton(text="👀 Посмотреть мнения", callback_data="opinion")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data = "stats_back")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
      
@router.callback_query(F.data == "opinion")
async def opinion_handler(callback: CallbackQuery):
    user_id = callback.from_user.id 
    
    exe = await get_results2(user_id)
    if not exe:
        await callback.answer("Увы у вас пока нету мнений")
        return
     
    buttons = []
    for i in range (1, len(exe)+1): #тут для меня i является переменнной для сверки сколько мнений есть и сколько их нужно создать
        buttons.append(
            InlineKeyboardButton(
                text = f"Мнение № {i}",
                callback_data = f"stats_view_{i}"
            )
    
        )
    step = [buttons[i:i+2] for i in range(0, len(buttons), 2)]
    step.append([
        InlineKeyboardButton(text="🔙 Назад", callback_data="stats_back")
    ])
    keyboard = InlineKeyboardMarkup(inline_keyboard=step)
    
    await callback.message.edit_text(
        "<b>😏 Ваши мнения:</b>",
        reply_markup = keyboard,
        parse_mode="HTML")
    await callback.answer()

    
    #await message.answer("😏 Ваши мнения:")
    # exe = await get_results2(user_id)
    # print(exe)
    
# @router.callback_query(F.data.startswith("stats_view_"))
# async def opinion_show_handler(callback:CallbackQuery):
#     bts = int(callback.data.split("_")[2]) - 1
#     print(bts)



@router.callback_query(F.data.startswith("stats_view_"))
async def opinion_show_handler(callback: CallbackQuery):
    user_id = callback.from_user.id
    index = int(callback.data.split("_")[2]) - 1

    results = await get_results2(user_id)
    #Начиная от строки 109 и до конца закоментированный скрипт является рабочим(все что я вводил это все пример для обьяснения самому себе)
    if index < 0 or index >= len(results):
        await callback.answer("Мнение не найдено")
        return
    
    result = results[index]
    sender_id = result["from_user_id"]
    sec_message = result["sec_message"] or "Пропущено"

    #ниже бллк конвертации
    raw_answers = result["answers"]
    print(raw_answers)

    if isinstance(raw_answers, list): #проверка на то, является ли raw_answers списоком, и если это список то конвертирует список в словарб
        answers = {
            "s_question_1": raw_answers[0] if len(raw_answers) > 0 else 0,
            "s_question_2": raw_answers[1] if len(raw_answers) > 1 else 0,
            "s_question_3": raw_answers[2] if len(raw_answers) > 2 else 0,
            "s_question_4": raw_answers[3] if len(raw_answers) > 3 else 0,
            "s_question_5": raw_answers[4] if len(raw_answers) > 4 else 0,
            "fact_value": raw_answers[5] if len(raw_answers) > 5 else "Пропущено",
            "anonymous": raw_answers[6] if len(raw_answers) > 6 else 1,
        }
    else:
        answers = raw_answers
    
    
    # # преобразование цифровых ответов в текст
    q1 = answer_list[1][answers.get("s_question_1", 0)]
    q2 = answer_list[2][answers.get("s_question_2", 0)]
    q3 = answer_list[3][answers.get("s_question_3", 0)]
    q4 = answer_list[4][answers.get("s_question_4", 0)]
    q5 = answer_list[5][answers.get("s_question_5", 0)]
    #fact_value = answers.get("fact_value", "Пропущено")
    fact_value = result.get("sec_message")
    if not fact_value or fact_value.strip() == "" or fact_value == "0":
        fact_value = "Пропущено"
    # имя отправителя
    # try:
    #     chat = await callback.bot.get_chat(sender_id)
    #     sender_name = chat.first_name
        
    # except:
    #     sender_name = "Аноним"
    # имя отправителя
    anonymous_flag = answers.get("anonymous", 1)  # 1 = аноним, 0 = не аноним

    if anonymous_flag == 1:
        sender_name = "Аноним"
    else:
        try:
            chat = await callback.bot.get_chat(sender_id)
            sender_name = chat.first_name
        except:
            sender_name = "Аноним"
        
    check_conclude = await check_relation(user_id, sender_id)
    
    text = (
        "🐣 <b>Новое мнение</b>\n"
        f"👤 <b>{sender_name}</b>\n\n"
        f"⭐️ <b>Ты для него/неё: {q1}</b>\n"
        f"🎀 <b>Нравится в тебе: {q2}</b>\n"
        f"😽 <b>Хочет: {q3}</b>\n"
        f"❓ <b>Знакомы: {q4}</b>\n"
        f"✌️ <b>Похожий смайлик: {q5}</b>\n"
        f"✉️ <b>Факт о тебе: {fact_value}</b>\n\n"
        "<b>Не забывай делиться классными ответами с друзьями, в историях и в тиктоке!</b>\n\n"
        "@opiniondevelopment_bot"
    )
    if check_conclude:
        keyboard = None
    else:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(
                text="🤩 Оценить в ответ",
                callback_data=f"back:{sender_id}"
        )
    ]])

    await callback.message.edit_text(
        text, 
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await callback.answer()
    
    
#-----OPINIONS команда находится здеся------
@router.message(Command("opinions"))
async def cmd_stats(message: Message):
    user_id = message.from_user.id
    print(user_id)
    
    exe = await get_results2(user_id)
    if not exe:
        await message.answer("Увы у вас пока нету мнений")
        return
     
    buttons = []
    for i in range (1, len(exe)+1): #тут для меня i является переменнной для сверки сколько мнений есть и сколько их нужно создать
        buttons.append(
            InlineKeyboardButton(
                text = f"Мнение № {i}",
                callback_data = f"stats_view_{i}"
            )
    
        )
    step = [buttons[i:i+2] for i in range(0, len(buttons), 2)]
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=step)
    await message.answer(
        "<b>😏 Ваши мнения:</b>",
        reply_markup = keyboard,
        parse_mode="HTML")
    #await callback.answer()
