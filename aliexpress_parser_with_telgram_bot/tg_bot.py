"""
пишем телегобота
"""

# импортируем все для написания бота
import json

from aiogram import Bot, Dispatcher, executor, types
# импортируем фильтр text для проверки совпадения текста кнопки
from aiogram.dispatcher.filters import Text
from lesson_15 import data_collection
# импортируем две функции hlink позволяет формировать ссылку с нужным названием, а hbold текст + вывод
from aiogram.utils.markdown import hbold, hlink

# токен бота
token = '[тут должен быть токен бота]'

# создаем объект бота, он принимает токен, метод parse_mode - чтобы скрывать теги json файлов при выводе
bot = Bot(token=token, parse_mode=types.ParseMode.HTML)
# создаем объект диспетчера (для управления хэндлерами)
dp = Dispatcher(bot)


# создаем функцию ответа на команду
@dp.message_handler(commands='start')
async def start(message: types.Message):
    # создадим список кнопок
    start_button = ['али', 'xbox', 'наушники']
    # создаем объект клавиатуры, параметр resize_keyboard=True - для маленького размера кнопок
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    # добавляем в клавиатуру список кнопок
    keyboard.add(*start_button)
    await message.answer("товары", reply_markup=keyboard)

# напишем хендлер для получения товаров из али
# функция реагирует на введенный текст, а ввод текста происходит по кнопке
@dp.message_handler(Text(equals='али'))
async def get_ali(message: types.Message):
    # отправим сообщение, чтобы чел ждал пока собираются данные
    await message.answer("Подожди мальца...")

    # вызываем функцию парсинга данных
    data_collection()

    # открываем файл на чтение
    with open('data.json', encoding='utf-8') as file:
        data = json.load(file)

    # бежим по списку карточек
    for item in data:
        # создаем карточку-сообщенией с построчным выводом
        # hlink - принимает текст, который выведет сообщением, и ссылку которая закрепиться к тексту
        # hbold принимает текст который выведет сообщением
        card = f'{hlink(item.get("description"), item.get("url"))}\n' \
               f'{hbold("цена на товар")} {item.get("price")}🔥'

        # отправляем сообщение
        await message.answer(card)




def main():
    executor.start_polling(dp)

if __name__ == "__main__":
    main()
