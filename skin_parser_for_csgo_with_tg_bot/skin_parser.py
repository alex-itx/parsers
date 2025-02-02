"""
парсим магазин скинов для игры cs:go и вставляем в бота
"""
import json
import time
import requests

headers = {
    'accept': 'application/json, text/plain, */*',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.115 Safari/537.36'
}

# функция сбора данных
# параметр card_type - изменяет парметр type в url он отвечает за то какой вид скинов мы ищем(2 - ножи, 4 - снайперки..)
def collect_data(card_type=2):

    # конечный список
    result_list = []
    # счетчик офсета
    offset = 0
    # цикл по скроллам
    while True:
        url = f'https://inventories.cs.money/5.0/load_bots_inventory/730?buyBonus=35&isStore=true&limit=60&maxPrice=10000&minPrice=2000&offset={offset}&sort=botFirst&type={card_type}&withStack=true'
        res = requests.get(url, headers=headers).json()

        # если на странице нет карточек
        if 'items' not in res:
            break

        # список карточек на странице
        items = res.get('items')
        # цикл по карточкам
        for item in items:

            # забираем только те карточки у которых скидка больше 10%
            if item['overprice'] is not None and item['overprice'] < -10:

                name = item['fullName']
                item_url = item.get('3d')
                price = item['price']
                overprice = item['overprice']

                result_list.append(
                    {
                        'name': name,
                        'url': item_url,
                        'price': price,
                        'overprice': overprice
                    }
                )


        print(f'{int(offset / 60 + 1)} страница обработана')

        # если карточек на странице меньше 60 значит это последняя страница
        if len(items) < 60:
            break

        offset += 60

    with open('result.json', 'w', encoding='utf-8') as file:
        json.dump(result_list, file, indent=4, ensure_ascii=False)


def main():
    start_time = time.time()

    collect_data(card_type=4)

    print(f'время работы скрипта - {time.time() - start_time}')


if __name__ == '__main__':
    main()
