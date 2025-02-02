"""
парсим каталог акций магазина магнит и заливаем данные в бота
"""

import requests
import csv
from datetime import datetime
from bs4 import BeautifulSoup
from time import time


def collect_data(city_code='1779'):
    """
    функция сбора данных каталога акций, магазина магнит в конкретном городе

    :param city_code: код города, является параметром при парсинге конкретного города,
     по дефолту стоит код города Новороссийск
    :return: возвращает сообщение о успешном окончание работы
    """

    # переменная хранящая время запуска программы, будет служить частью имени в файле данных
    cur_time = datetime.now().strftime('%d_%m_%Y_%H_%M')

    url = 'https://magnit.ru/promo/?category[]=alk'

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
    }

    # в куки хранится информация о городе который мы парсим, в него и будем вставлять id города - city_code=
    cookies = {
        'mg_geo_id': city_code
    }

    # подключаемся к сайту и создаем объект парсера
    res = requests.get(url, headers=headers, cookies=cookies).text
    soup = BeautifulSoup(res, 'lxml')

    # забираем название города
    city = soup.find(class_="header__contacts-text").text.strip()

    # забираем карточки товаров
    cards = soup.find_all(class_="card-sale")

    # создаем csv файл
    with open(f'{cur_time}_data.csv', 'w', encoding='utf-8') as file:
        writer = csv.writer(file)

        writer.writerow(
            (
                'продукт',
                'старая цена',
                'новая цена',
                'скидка',
                'срок акции'
            )
        )

    # дозаписываем csv файл
    with open(f'{cur_time}_data.csv', 'a', encoding='utf-8') as file:
        writer = csv.writer(file)

        # бежим по каждой карточке
        for card in cards:

            # забираем процент скидки, если ее нет, то пропускаем данную карточку
            try:
                sale = card.find(class_="label label_sm label_mextra card-sale__discount").text
            except AttributeError:
                continue

            # забираем название карточки
            title = card.find(class_="card-sale__title").text.strip()

            # забираем старую цену
            old_price_integer = card.find(class_="label__price label__price_old").find(class_="label__price-integer").text
            old_price_decimal = card.find(class_="label__price label__price_old").find(class_="label__price-decimal").text
            old_price = f'{old_price_integer}.{old_price_decimal}'

            # забираем новую цену
            new_price_integer = card.find(class_="label__price label__price_new").find(class_="label__price-integer").text
            new_price_decimal = card.find(class_="label__price label__price_new").find(class_="label__price-decimal").text
            new_price = f'{new_price_integer}.{new_price_decimal}'

            # забираем срок акции
            action_period = card.find(class_="card-sale__date").text.strip().replace('\n', ' - ')

            # записываем данные в файл
            writer.writerow(
                (
                    title,
                    old_price,
                    new_price,
                    sale,
                    action_period
                )
            )

    return 'данные собраны!'


def main():
    print(collect_data())




if __name__ == '__main__':
    main()
