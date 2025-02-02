"""
парсим сайт-книжный магазин
"""

import requests, lxml, os, time, json, csv
from bs4 import BeautifulSoup
from datetime import datetime


start_time = time.time()
def get_data():
    cur_time = datetime.now().strftime("%d_%m_%Y_%H_%M")

    with open(f'labirint_{cur_time}.csv', 'w', encoding='utf-8') as file:
        writer = csv.writer(file)

        writer.writerow(
            (
                'название',
                "автор",
                "издатель",
                "цена",
                "старая цена",
                "скидка",
                "статус"
            )
        )

    headers = {
        'accept': 'text/html, */*; q=0.01',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36'
    }
    url = 'https://www.labirint.ru/genres/2308/?page=1&available=1&preorder=1&paperbooks=1&otherbooks=1&display=table'
    req = requests.get(url, headers=headers)
    res = req.text

    soap = BeautifulSoup(res, 'lxml')

    # ищем последнюю страницу
    last_page = soap.find(class_="pagination-number").find_all('a')[-1].text


    # конечный список книг
    books_data = []

    for page in range(1, int(last_page) + 1):
    # for page in range(2, 3):

        url = f'https://www.labirint.ru/genres/2308/?page={page}&available=1&preorder=1&paperbooks=1&otherbooks=1&display=table'
        req = requests.get(url, headers=headers)
        res_page = req.text

        soap = BeautifulSoup(res_page, 'lxml')

        books_items = soap.find(class_="products-table__body").find_all('tr')

        for book in books_items:

            # ищем название книги
            try:
                name = book.find_all('a')[0].text
            except:
                name = 'Нет названия'

            # ищем автора
            try:
                author = book.find_all('a')[1].text
            except:
                author = 'Нет автора'

            # ищем издателя
            try:
                publishing = book.find(class_="products-table__pubhouse col-sm-2").find_all('a')
                publishing = ':'.join([pb.text for pb in publishing])
            except:
                publishing = 'Нет издателя'

            # ищем цену
            try:
                price = book.find(class_="price").find('span').find('span').text.replace(" ", '')
            except:
                price = 'нет цены'

            # ищем староую цену
            try:
                old_price = book.find(class_="price-old").find('span').text.replace(" ", '')
            except:
                old_price = 'нет старой цены'

            # ищем процент скидки
            try:
                sale = round((int(old_price) - int(price)) / (int(old_price) / 100))
            except:
                 sale = 'нет скидки'

            # ищем информацию о наличии
            try:
                status = book.find_all('div')[-1].text.strip()
            except:
                status = 'Нет статуса'

            books_data.append(
                {
                    'title': name,
                    'author': author,
                    'publishing': publishing,
                    'price': price,
                    'old_price': old_price,
                    'sale': sale,
                    'status': status
                }
            )

            with open(f'labirint_{cur_time}.csv', 'a', encoding='utf-8') as file:
                writer = csv.writer(file)

                writer.writerow(
                    (
                        name,
                        author,
                        publishing,
                        price,
                        old_price,
                        sale,
                        status
                    )
                )

        print(f'страница {page} из {last_page} обработана')

        # time.sleep(1)

    with open(f'labirint_{cur_time}.json', 'a', encoding='utf-8') as file:
        json.dump(books_data, file, indent=4, ensure_ascii=False)

    finish_time = time.time() - start_time

    print(f'время работы - {finish_time}')

def main():
    get_data()

if __name__ == '__main__':
    main()
