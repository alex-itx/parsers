"""
парсинг магазина шин
прикрепленный json к странице
достаем инфу из json и парсим через него
"""

import requests, lxml, os, time, json, csv
from bs4 import BeautifulSoup
from datetime import datetime

"""
поковырявшись во вкладке network страницы, нашёл в ответе одного из запросов, ссылку на json страницу, 
в которой хранится вся информация о шинах и даже пагинация в более удобной форме для сбора информации,
чем через html страницу
в запроси было два заголовка которые нам нужны для преобразования страницы - X-Is-Ajax-Request и X-Requested-With
их и будем использовать при гет-запросе, а парсить информацию уже с этой страницы
"""
headers = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'X-Is-Ajax-Request': 'X-Is-Ajax-Request',
    'X-Requested-With': 'XMLHttpRequest',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36'
}

def get_data():
    # сначала сохраним в переменную текущее время,
    # а в конце программы, вычтем его из текущего времени на момент конца работы программы
    start_time = datetime.now()

    url = 'https://roscarservis.ru/catalog/legkovye/?isAjax=true'
    req = requests.get(url, headers=headers)
    res = req.json()

    # with open('index.json', 'w', encoding='utf-8') as file:
    #     json.dump(res, file, indent=4, ensure_ascii=False)

    """
    сначала вытаскиваем пагинацию чтобы потом итерироваться по всем страницам,
    """
    pages_count = res['pageCount']

    """создаем список ключей складов чтобы потом итерироваться по ним и добавлять каждый склад"""
    possible_stores = ['discountStores', 'fortochkiStores', 'commonStores']

    # конечный список всех шин
    data_list = []

    # for page in range(1, pages_count - (pages_count - 3)):
    for page in range(1, pages_count + 1):
        url = f'https://roscarservis.ru/catalog/legkovye/?isAjax=true&PAGEN_1={page}'
        req_items = requests.get(url, headers=headers)

        # ключь хроннящий каждую шину на странице
        items = req_items.json()['items']

        # вытаскиваем все необхадимое из каждой шины
        for item in items:
            # общее количество всех шин на всех складах
            total_amount = 0

            item_name = item['name']
            item_price = item['price']
            item_img = f'https://roscarservis.ru{item["imgSrc"]}'
            item_url = f'https://roscarservis.ru{item["url"]}'

            # список всех складов с их названиями, количеством шин в них,
            # и ценами на шину в них(она может отличаться на разных складах)
            stores = []
            # итерируемся по всем ключам складов в json
            for ps in possible_stores:
                # проверка на то что у шины есть ключ складов,
                # а далее на то что этот ключ не пустой
                if ps in item:
                    if item[ps] is None or len(item[ps]) < 1:
                        continue
                    else:
                        # вытаскиваю всю инфу с каждого склада
                        for store in item[ps]:
                            store_name = store['STORE_NAME']
                            store_price = store['PRICE']
                            store_amount = store['AMOUNT']
                            total_amount += int(store['AMOUNT'])

                        # добавляем в список складов
                            stores.append(
                                {
                                    'store_name': store_name,
                                    'store_price': store_price,
                                    'store_amount': store_amount
                                }
                            )

            # добавляем все собранное о шине в список шин
            data_list.append(
                {
                    'name': item_name,
                    'price': item_price,
                    'img_url': item_img,
                    'url': item_url,
                    'total_amount': total_amount,
                    'stores': stores
                }
            )


        # отслеживаем прогресс парсинга страниц
        # print(f'страница {page} из {pages_count - 1 - (pages_count - 3)} обработана')
        print(f'страница {page} из {pages_count} обработана')



    # дату и время для названия файла
    cur_time = datetime.now().strftime('%d_%m_%Y_%H_%M')
    # далее записываем список json
    with open(f'data_{cur_time}.json', 'a', encoding='utf-8') as file:
        json.dump(data_list, file, indent=4, ensure_ascii=False)

    # узнаем сколько работала наша программа
    diff_time = datetime.now() - start_time
    print(f'время работы - {diff_time}')

def main():
    get_data()

if __name__ == '__main__':
    main()
