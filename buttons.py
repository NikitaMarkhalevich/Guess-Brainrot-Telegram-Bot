from aiogram.types import (InlineKeyboardButton, InlineKeyboardMarkup,
                           KeyboardButton, ReplyKeyboardMarkup)
from random import *

start_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Начать Угадывать!')]
], resize_keyboard=True)

start_again_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Начать Занаво!')]
], resize_keyboard=True) 

continue_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Начать Занаво!')],
    [KeyboardButton(text='Продолжить')]
], resize_keyboard=True)

admin_panel_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Добавить мем', callback_data='add_meme')],
    [InlineKeyboardButton(text='Список мемов', callback_data='memes_list')]
])

def make_answer_kb(correct_answer: str, all_answers: list):
    wrong_answers = [a for a in all_answers if a != correct_answer]
    shuffle(wrong_answers)
    options = wrong_answers[:3] + [correct_answer]
    shuffle(options)

    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text=opt) for opt in options],
        [KeyboardButton(text='Пропустить: 5 очков')],
        [KeyboardButton(text='Стоп')],
        [KeyboardButton(text='Пропустить всё')]
    ], resize_keyboard=True)
    return kb
