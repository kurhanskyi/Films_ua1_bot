from aiogram.utils.keyboard import InlineKeyboardBuilder

def build_films_keyboard(films: list):
    builder = InlineKeyboardBuilder()
    for index, film in enumerate(films):
        builder.button(text=film.get("title"), callback_data=f"film_{index}")
    return builder.as_markup()

def build_details_keyboard(url):
    builder = InlineKeyboardBuilder()
    builder.button(text="Перейти за посиланням", url=url)
    builder.button(text="Повернутись назад", callback_data="back")
    return builder.as_markup()

def build_menu_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="Повернутись назад", callback_data="back")
    return builder.as_markup()



