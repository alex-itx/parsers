"""
пишем бота для проекта
t.me/magnit_646615_bot
"""

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text
from assinc_pars import collect_data

bot = Bot(token='[тут должен быть токен]')
dp = Dispatcher(bot)

# функция старт
@dp.message_handler(commands='start')
async def start(message: types.Message):
    start_button = ['Новороссийск', "Москва"]
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*start_button)

    await message.answer('Выбери город', reply_markup=keyboard)

# функция ответа на новороссийск
@dp.message_handler(Text(equals="Новороссийск"))
async def novoros(message: types.Message):
    await message.answer('жди')
    # получаем чат айди что бы потом отправлять файл конкретному пользователю
    chat_id = message.chat.id
    # вызываем функцию отправления документа
    await send_data(chat_id=chat_id)

# функция ответа на москва
@dp.message_handler(Text(equals="Москва"))
async def moscow(message: types.Message):
    await message.answer('жди')
    chat_id = message.chat.id
    await send_data(city_code='2398', chat_id=chat_id)

# функция которая вызывает парсер и передает файл с данными
# принимает код города и чат айди
async def send_data(city_code='1779', chat_id=''):
    file = await collect_data(city_code=city_code)
    # отправляем файл пользователю методом send_document()
    # метод принимает чат id и документ открытый на чтение в двоичном режиме
    await bot.send_document(chat_id=chat_id, document=open(file, 'rb'))


if __name__ == '__main__':
    executor.start_polling(dp)
