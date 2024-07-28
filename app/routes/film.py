from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.utils.markdown import hbold
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from fuzzywuzzy import fuzz

from ..data import *
from ..fsm import FilmCreateForm, FilmDeleteForm
from ..keyboards import *

film_router = Router()

@film_router.message(Command("films"))
@film_router.message(F.text.casefold().contains("films"))
async def show_films_command(message: Message, state: FSMContext):
    films = get_films()
    keyboard = build_films_keyboard(films)

    await message.answer(
        text="Виберіть будь-який фільм",
        reply_markup=keyboard,
    )


@film_router.callback_query(F.data.startswith("film_"))
async def show_film_details(callback: CallbackQuery, state: FSMContext) -> None:
    film_id = int(callback.data.split("_")[-1])
    film = get_film(film_id)
    text = f"Назва: {hbold(film.get('title'))}\nОпис: {hbold(film.get('desc'))}\nРейтинг: {hbold(film.get('rating'))}"
    photo_id = film.get('photo')
    url = film.get('url')
    await callback.message.answer_photo(photo_id)
    await edit_or_answer(callback.message, text, build_details_keyboard(url))


async def edit_or_answer(message: Message, text: str, keyboard, *args, **kwards):
    if message.from_user.is_bot:
        await message.edit_text(text=text, reply_markup=keyboard, **kwards)
    else:
        await message.answer(text=text, reply_markup=keyboard, **kwards)

@film_router.message(Command("filmcreate"))
@film_router.message(F.text.casefold() == "filmcreate")
@film_router.message(F.text.casefold() == "create film")
async def create_film_command(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.update_data(action='create')
    await state.set_state(FilmCreateForm.title)
    await edit_or_answer(
        message,
        "Введіть назву фільму",
        ReplyKeyboardRemove()
    )

@film_router.message(FilmCreateForm.title)
async def process_title(message: Message, state: FSMContext) -> None:
    await state.update_data(title=message.text)
    await state.set_state(FilmCreateForm.desc)
    await edit_or_answer(
        message,
        "Введіть опис фільму",
        ReplyKeyboardRemove()
    )

@film_router.message(FilmCreateForm.desc)
async def process_desc(message: Message, state: FSMContext) -> None:
    data = await state.update_data(desc=message.text)
    await state.set_state(FilmCreateForm.url)
    await edit_or_answer(
        message,
        f"Введіть посилання на фільм {hbold(data.get('title'))}",
        ReplyKeyboardRemove()
    )

@film_router.message(FilmCreateForm.url)
@film_router.message(F.text.contains('http'))
async def process_url(message: Message, state: FSMContext) -> None:
    data = await state.update_data(url=message.text)
    await state.set_state(FilmCreateForm.photo)
    await edit_or_answer(
        message,
        f"Надайте фотографію для афіші фільму {hbold(data.get('title'))}",
        ReplyKeyboardRemove()
    )

@film_router.message(FilmCreateForm.photo)
@film_router.message(F.photo)
async def process_photo(message: Message, state: FSMContext) -> None:
    photo = message.photo[-1]
    photo_id = photo.file_id

    data = await state.update_data(photo=photo_id)
    await state.set_state(FilmCreateForm.rating)
    await edit_or_answer(
        message,
        "Надайте рейтинг фільму",
        ReplyKeyboardRemove()
    )

@film_router.message(FilmCreateForm.rating)
async def process_rating(message: Message, state: FSMContext) -> None:
    data = await state.update_data(rating=message.text)

    action = (await state.get_data()).get('action')

    if action == 'create':
        save_film(data)
    elif action == 'update':
        title = data.get('title')

        yes_or_no = update_film(title, data)
        if yes_or_no:
            await message.answer("Оновлено успішно")
        else:
            await message.answer("Введіть коректну назву")

    await state.clear()
    return await show_films_command(message, state)

@film_router.callback_query(F.data == 'back')
async def back_handler(callback: CallbackQuery, state: FSMContext) -> None:
    return await show_films_command(callback.message, state)

@film_router.message(Command('filmdelete'))
@film_router.message(F.text.casefold() == 'delete film')
async def delete_film_command(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(FilmDeleteForm.title)
    await edit_or_answer(
        message,
        "Введіть назву фільму",
        ReplyKeyboardRemove()
    )

@film_router.message(FilmDeleteForm.title)
async def process_delete_film(message: Message, state: FSMContext) -> None:
    await state.update_data(title=message.text)
    title = (await state.get_data()).get('title')
    await state.clear()

    if title:
        delete_film(title)
    else:
        edit_or_answer(
            message,
            "Не вдалося отримати назву фільму"
        )

    return await show_films_command(message, state)

@film_router.message(Command('filmupdate'))
@film_router.message(F.text.casefold() == 'update film')
async def update_film_command(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.update_data(action='update')
    await state.update_data(FilmCreateForm.title)
    await message.answer(
        "Введіть назву фільму",
        reply_markup=ReplyKeyboardRemove()
    )


@film_router.message(Command("search"))
@film_router.message(F.text.casefold().startswith("search "))
async def search_film(message: Message, state: FSMContext):
    search_query = message.text.split("search ", 1)[1].strip().lower() if " " in message.text else ""
    films = get_films()

    matching_films = []
    for film in films:
        title = film.get('title', '').lower()
        ratio = fuzz.partial_ratio(search_query, title)
        if ratio > 60:
            matching_films.append((film, ratio))

    matching_films.sort(key=lambda x: x[1], reverse=True)

    if matching_films:
        response = "Знайдені фільми:\n\n"
        for film, ratio in matching_films[:5]:
            response += f"- {hbold(film['title'])} \n"
        await message.answer(response, parse_mode="HTML")
    else:
        await message.answer("На жаль, фільмів за вашим запитом не знайдено.")