from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from random import choice
from database import *

from buttons import *

from dotenv import load_dotenv
import os
load_dotenv() 

label = 'https://c.tenor.com/Ns-WiLu5d5IAAAAC/tenor.gif'

router = Router()

class Game(StatesGroup):
    wait_for_answer = State()

class AddNewMeme(StatesGroup):
    name = State()
    url = State()

def get_unused_memes(used_urls):
    if not used_urls:
        cursor.execute('SELECT name, url FROM memes')
    else:
        placeholder = ','.join('?' for _ in used_urls)
        cursor.execute(f'SELECT name, url FROM memes WHERE url NOT IN ({placeholder})', used_urls)
    return cursor.fetchall()

def get_all_memes():
    cursor.execute('SELECT name, url FROM memes')
    return cursor.fetchall()

async def send_new_meme(message: Message, state: FSMContext):
    data = await state.get_data()
    used = data.get('used_photos', [])
    guessed_count = data.get('guessed_count', 0)
    skipped = data.get('skipped', 0)
    incorrect = data.get('incorrect', 0)

    remaining = get_unused_memes(used)
    if not remaining:
        await message.answer_animation(animation='https://c.tenor.com/yxmqzjBCxcgAAAAC/tenor.gif',
                                       caption=f'🤩 Ты угадал {guessed_count} мемов, не угадал {incorrect} мемов и пропустил {skipped} мемов! 🤩',
                                       reply_markup=start_again_kb)
        await state.clear()
        return

    meme_name, meme_url = choice(remaining)

    answer_kb = make_answer_kb(meme_name, [n[0] for n in get_all_memes()])

    await message.answer_photo(photo=meme_url,
                            caption='🤔 Кто это? 🤔', 
                            reply_markup=answer_kb)

    used.append(meme_url)
    await state.update_data(
        correct_answer=meme_name,
        used_photos=used,
        last_meme_name=meme_name,
        last_meme_url=meme_url,
        last_kb=answer_kb)
    
    await state.set_state(Game.wait_for_answer)

@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer_animation(animation=label,
    caption=f'👋 Привет! 👋 \n😹В этом боте нужно угадать Брейнрот мем!😹\n💸С каждым угаданным мемов твой баланс пополняется!💸\nАвтор - @Nekit_Kisame\n', reply_markup=start_kb)

@router.message(F.text == 'Начать Угадывать!')
async def start_guess(message: Message, state: FSMContext):
    await message.answer('Погнали!')
    await send_new_meme(message, state)

@router.message(F.text == 'Начать Занаво!')
async def start_again(message: Message, state: FSMContext):
    await state.clear()
    await message.answer('Начинаем Занаво!')
    await send_new_meme(message, state)
    await state.set_state(Game.wait_for_answer)

@router.message(Command('admin'))
async def admin_panel(message: Message):
    if message.from_user.username == os.getenv('ADMIN'):
        await message.answer('Вот админ панель', reply_markup=admin_panel_kb)
    else:
        await message.answer('Ты не админ! Нельзя!')

@router.callback_query(F.data == 'add_meme')
async def ask_new_meme(callback_querry: CallbackQuery, state: FSMContext):
    await callback_querry.answer()
    await callback_querry.message.answer('Название мема', reply_markup=ReplyKeyboardRemove())
    await state.set_state(AddNewMeme.name)

@router.callback_query(F.data == 'memes_list')
async def send_memes_list(callback_querry: CallbackQuery):
    await callback_querry.answer()
    all_memes_names = [n[0] for n in get_all_memes()]
    await callback_querry.message.answer(f'{', '.join(all_memes_names)}', reply_markup=ReplyKeyboardRemove())

@router.message(AddNewMeme.name)
async def send_new_meme_name(message: Message, state: FSMContext):
    new_meme_name = message.text
    await state.get_data()
    await state.update_data(new_meme_name=new_meme_name)
    await message.answer(f'Название нового мема {new_meme_name}! \nТеперь отправь Ссылка на картинку\n')
    await state.set_state(AddNewMeme.url)

@router.message(AddNewMeme.url)
async  def send_new_meme_url(message: Message, state: FSMContext):
    new_meme_url = message.text
    data = await state.get_data()
    new_meme_name = data.get('new_meme_name')
    cursor.execute('INSERT INTO memes (name, url) VALUES (?, ?)', (f'{new_meme_name}',f'{new_meme_url}'))
    conn.commit()
    cursor.close()
    await state.update_data(new_meme_url=new_meme_url)
    await message.answer(f'Отлично!\nНазвание мема {new_meme_name}\nИ ссылка {new_meme_url}\n')

@router.message(Game.wait_for_answer)
async def check_answer(message: Message, state: FSMContext):
    data = await state.get_data()
    correct_answer = data.get('correct_answer', '')
    user_answer = message.text

    score = data.get('score', 0)
    trys = data.get('trys', 3)
    guessed_count = data.get('guessed_count', 0)
    skipped = data.get('skipped', 0)
    incorrect = data.get('incorrect', 0)
    last_meme_name = data.get('last_meme_name')
    last_meme_url = data.get('last_meme_url')
    used = data.get('used_photos', [])
    last_kb = data.get('last_kb')

    if user_answer == 'Стоп':
        await message.answer('Игра завершена', reply_markup=continue_kb)   

    elif user_answer == 'Пропустить всё':
        skipped = len([n[0] for n in get_all_memes()]) - guessed_count
        await message.answer(f'Ты пропустил {skipped} мемов!',
                            reply_markup=start_again_kb)
        await state.clear()

    elif user_answer == correct_answer:
        score += 5
        guessed_count += 1
        await message.answer(f'Ты угадал!🎆😃 Это {correct_answer}!\nБаланс: {score}💰\n')

        await state.update_data(score=score, guessed_count=guessed_count, trys=3)
        await send_new_meme(message, state)
        await state.set_state(Game.wait_for_answer)

    elif user_answer == 'Пропустить: 5 очков':
        if score >= 5:
            skipped += 1
            score -= 5
            await message.answer(f'Пропускаем! \nБаланс: {score}💰\n')
            used.append(last_meme_url)
            await state.update_data(score=score, 
                                    skipped=skipped, 
                                    trys=3, 
                                    used_photos=used)
            await send_new_meme(message, state)
            await state.set_state(Game.wait_for_answer)
        else:
            await message.answer('Нельзя пропустить! Угадывай давай!')

    elif user_answer == 'Продолжить':
        await message.answer_photo(photo=last_meme_url,
                                caption='🤔 Кто это? 🤔', 
                                reply_markup=last_kb)

        used.append(last_meme_url)
        await state.update_data(
            correct_answer=last_meme_name,
            used_photos=used,
            last_meme_name=last_meme_name,
            last_meme_url=last_meme_url,
            last_kb=last_kb)
        
        await state.set_state(Game.wait_for_answer)

    else:
        trys -= 1
        if trys > 0:
            await message.answer(f'Не угадал!❌😲 Попробуй ещё {trys} раз(а)')
            await state.update_data(trys=trys)
        else:
            if score > 0:
                score -= 5
            await message.answer(f'Не угадал!❌😲 Это {correct_answer}!\nБаланс: {score}💰\n')
            trys = 3
            incorrect += 1
            await state.update_data(score=score, trys=trys, used_photos=used, incorrect=incorrect)
            await send_new_meme(message, state)
            await state.set_state(Game.wait_for_answer)


