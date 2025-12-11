from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from handlers.message_origin import user_link

router = Router()

@router.message(F.text == "/help")
async def cmd_help(message: Message):
    user_id = message.from_user.id
    test_link, share_url = user_link(user_id)
    
    text = (("<b>📲 Чтобы получать МНЕНИЯ от друзей/знакомых тебе нужно разместить ссылку в своём профиле и в соц. сетях!</b>\n\n"
    f"👉{test_link}"

    ))
    await message.answer(text, parse_mode="HTML")