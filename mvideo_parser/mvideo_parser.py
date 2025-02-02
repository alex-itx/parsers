"""
парсим магазин мвидео
"""

import requests, json
from bs4 import BeautifulSoup as BS
# функция достает api, который хранит ID товаров и записывает их в json
from get_json_from_listing import get_ids
from get_json_from_list import get_data_products
from get_json_from_price import get_price

url = 'https://www.mvideo.ru/noutbuki-planshety-komputery-8/planshety-195/f/skidka=da/tolko-v-nalichii=da'



def get_data():
    """
    функция сбора всех данных
    :return: сообщение об успешном завершение работы функции
    """
    # запускаем функцию сбора id
    get_ids()

    # сохраняем список id в переменную
    with open('ids.json', encoding='utf-8') as file:
        ids = json.load(file)

    # запускаем функцию сбора данных по продуктам
    get_data_products(ids)
    # запускаем функцию сбора цен по продуктам
    get_price(ids)

    return 'все данные собраны!'

def result_data():
    """
    функция объединения данных в единый файл с данными
    :return: сообщение об успешном завершение работы функции
    """
    # сохраняем список данных о продукте в переменную
    with open('data_products.json', encoding='utf-8') as file:
        products_data = json.load(file)

    # сохраняем список цен продуктов в переменную
    with open('price.json', encoding='utf-8') as file:
        price_list = json.load(file)

    # проходим по каждому продукту из списка с данными
    for product in products_data:
        # сохраняем id
        id_product = product.get("productId")

        # если id в списке списка цен как ключ
        if id_product in price_list:
            # сохраняем значению ключа
            price = price_list.get(id_product)

            # записываем к продукту в списке данных ключ price и значение price из списка цен
            product['price'] = price.get('price')
            # ключ old_price и значение old_price из списка цен
            product['old_price'] = price.get('old_price')
            # ключ bonus и значение bonus из списка цен
            product['bonus'] = price.get('bonus')

    # сохраняем объединённые products_data и price_list в один файл
    with open('result.json', 'w', encoding='utf-8') as file:
        json.dump(products_data, file, indent=4, ensure_ascii=False)

    return 'данные объединены!'


def main():
    print(get_data())
    print(result_data())


if __name__ == '__main__':
    main()
