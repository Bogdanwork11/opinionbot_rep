from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Router

router = Router()
storage = MemoryStorage()

class FSMTest(StatesGroup):
    create_state_initial = State() #для первого пользователя
    f_question_1 = State()
    f_question_2 = State()
    f_question_3 = State()
    f_question_4 = State()
    f_question_5 = State()
    f_question_6 = State()
    f_question_7 = State()
    f_test_created_final = State() #итог первого пользователя
    
    waiting_fact = State()#Создал для того чтобы получить в 6 вопросе состояние о сообщении
    
    create_state_secondary = State()
    s_question_1 = State()
    s_question_2 = State()
    s_question_3 = State()
    s_question_4 = State()
    s_question_5 = State()
    s_question_6 = State()
    secmes_s_question_6 = State()
    s_question_7 = State()
    question_pil = State()
    final_s_question = State()

class FSMsend(StatesGroup):
    mail_text = State()