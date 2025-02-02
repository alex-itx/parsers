"""
Асинхронный вариант
"""

import requests
import csv
from datetime import datetime
from bs4 import BeautifulSoup
from time import time
import aiogram, asyncio, aiocsv, aiohttp, aiofiles
# импортируем асинхронного писателя
from aiocsv import AsyncWriter

# это что бы IDE не ругался когда мы работаем асинхронно на винде
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Изменение
async def collect_data(city_code='1779'):
    """
    функция сбора данных каталога акций, магазина магнит в конкретном городе

    :param city_code: код города, является параметром при парсинге конкретного города,
     по дефолту стоит код города Новороссийск
    :return: возвращает сообщение о успешном окончание работы
    """

    cur_time = datetime.now().strftime('%d_%m_%Y_%H_%M')

    url = 'https://magnit.ru/promo/?category[]=alk'

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
    }

    cookies = {
        'mg_geo_id': city_code
    }

    # Изменение
    async with aiohttp.ClientSession() as session:

        # Изменение
        res = await session.get(url, headers=headers, cookies=cookies)
        soup = BeautifulSoup(await res.text(), 'lxml')

        city = soup.find(class_="header__contacts-text").text.strip()

        cards = soup.find_all(class_="card-sale")

        # Изменение
        async with aiofiles.open(f'{city}_{cur_time}.csv', 'w', encoding='utf-8') as file:
            # Изменение
            writer = AsyncWriter(file)

            # Изменение
            await writer.writerow(
                (
                    'продукт',
                    'старая цена',
                    'новая цена',
                    'скидка',
                    'срок акции'
                )
            )


    # Изменение
    async with aiofiles.open(f'{city}_{cur_time}.csv', 'a', encoding='utf-8') as file:
        # Изменение
        writer = AsyncWriter(file)

        for card in cards:

            try:
                sale = card.find(class_="label label_sm label_mextra card-sale__discount").text
            except AttributeError:
                continue

            title = card.find(class_="card-sale__title").text.strip()

            old_price_integer = card.find(class_="label__price label__price_old").find(class_="label__price-integer").text
            old_price_decimal = card.find(class_="label__price label__price_old").find(class_="label__price-decimal").text
            old_price = f'{old_price_integer}.{old_price_decimal}'

            new_price_integer = card.find(class_="label__price label__price_new").find(class_="label__price-integer").text
            new_price_decimal = card.find(class_="label__price label__price_new").find(class_="label__price-decimal").text
            new_price = f'{new_price_integer}.{new_price_decimal}'

            action_period = card.find(class_="card-sale__date").text.strip().replace('\n', ' - ')

            # Изменение
            await writer.writerow(
                (
                    title,
                    old_price,
                    new_price,
                    sale,
                    action_period
                )
            )

    # Изменение (для бота)
    return f'{city}_{cur_time}.csv'

# Изменение
async def main():
    await collect_data()

# Изменение
if __name__ == '__main__':
    asyncio.run(main())
