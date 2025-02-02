"""
Асинхронный авриант парсера
"""

import requests, lxml, os, time, json, csv, asyncio, aiohttp
from bs4 import BeautifulSoup
from datetime import datetime

start_time = time.time()

# конечный список книг
books_data = []

# тело функции наполняется после второй функции саму функцию объявляем с ключевым словом async
# парсер который пробегает по странице и собирает данные,
# основная задача
async def get_page_data(session, page):
    # вставляем загаловки и url с параметром page
    headers = {
        'accept': 'text/html, */*; q=0.01',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36'
    }

    url = f'https://www.labirint.ru/genres/2308/?page={page}&available=1&preorder=1&paperbooks=1&otherbooks=1&display=table'

    # отправляем запрос на url и сохраняем его текст асинхронным методом
    async with session.get(url=url, headers=headers) as req:
        res = await req.text()

        # далее копируем наш старый парсер
        soap = BeautifulSoup(res, 'lxml')

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

        print(f'страница {page} обработана')



# тело функции наполняется первой
# функция формирует список задач
async def gather_data():
    # берем старые заголовки и url
    headers = {
        'accept': 'text/html, */*; q=0.01',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36'
    }
    url = 'https://www.labirint.ru/genres/2308/?page=1&available=1&preorder=1&paperbooks=1&otherbooks=1&display=table'

    # создаем клиент сессию, которая позволяет повторно использовать уже открытое соединение
    async with aiohttp.ClientSession() as session:

        # находим общее количество страниц, используя старый код, но через асинхронный метод
        # для наглядности старый код чтобы увидеть разницу -
        # res = requests.get(url, headers=headers)
        # soap = BeautifulSoup(res.text, 'lxml')

        res = await session.get(url, headers=headers)
        soap = BeautifulSoup(await res.text(), 'lxml')

        last_page = int(soap.find(class_="pagination-number").find_all('a')[-1].text)

        # формируем список задач
        tasks = []

        # пробегаем по страницам сайта
        for page in range(1, last_page + 1):
            """
            создаем задачу используя метод create_task() библиотеки asyncio
            внутри которой будет наша функция парсер gather_data(),
            которая принимает в себя два параметра - объект сессии и текущую страницу пагинации
            """
            task = asyncio.create_task(get_page_data(session, page))
            # пополняем список задач
            tasks.append(task)

        # после завершения цикла, собираем задачи используя метод gather() библиотеки asyncio
        await asyncio.gather(*tasks)

def main():
    # лечилка для запуска без ошибок первого варианта запуска программы
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    cur_time = datetime.now().strftime("%d_%m_%Y_%H_%M")

    # для запуска используется метод run() библиотеки asyncio, он принимает функцию, которая исполняет программу
    # программа работает но в конце вылетает ошибка не влияющая на работу программы
    asyncio.run(gather_data())
    # второй способ запуска, но он тоже с ошибкой)
    # asyncio.get_event_loop().run_until_complete(gather_data())

    # запишем в json
    with open(f'labirint_{cur_time}_async.json', 'a', encoding='utf-8') as file:
        json.dump(books_data, file, indent=4, ensure_ascii=False)

    # теперь в csv
    with open(f'labirint_{cur_time}_async.csv', 'w', encoding='utf-8') as file:
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

    # дозаписывать будем здесь-же, циклом из списка книг
    for book in books_data:
        with open(f'labirint_{cur_time}_async.csv', 'a', encoding='utf-8') as file:
            writer = csv.writer(file)

            writer.writerow(
                (
                    book['title'],
                    book['author'],
                    book['publishing'],
                    book['price'],
                    book['old_price'],
                    book['sale'],
                    book['status']
                )
            )

    finish_time = time.time() - start_time
    print(f'время работы - {finish_time}')


if __name__ == '__main__':
    main()
