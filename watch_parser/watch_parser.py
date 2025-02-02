"""
парсим магазин часов,
вытаскиваем информацию о часах
"""
import requests, lxml, os, time, json, csv
from bs4 import BeautifulSoup
from datetime import datetime

def get_all_pages():
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36'
    }
    url = 'https://shop.casio.ru/catalog/g-shock/filter/gender-is-male/apply/'

    req = requests.get(url, headers=headers)
    res = req.text

    if not os.path.exists('data'):
        os.mkdir('data')

    with open('data/page_1.html', 'w', encoding='utf-8') as file:
        file.write(res)

    with open('data/page_1.html', encoding='utf-8') as file:
        src = file.read()

    soap = BeautifulSoup(src, 'lxml')

    """
    находим последнюю страницу в каталоге
    """
    pages_count = int(soap.find('div', class_="bx-pagination-container").find_all('a')[-2].text)

    """
    сохраняем каждую страницу
    """
    for i in range(1, pages_count + 1):
        url = f'https://shop.casio.ru/catalog/g-shock/filter/gender-is-male/apply/?PAGEN_1={i}'

        req = requests.get(url, headers=headers)
        res = req.text

        with open(f'data/page_{i}.html', 'w', encoding='utf-8') as file:
            file.write(res)

        # пауза что бы успевать прогружать страницы
        time.sleep(2)

    return pages_count + 1

def collect_data(pages_count):
    # создадим сохраним текущую дату в переменную для записи названия файла
    cur_date = datetime.now().strftime('%d_%m_%Y')

    with open(f'data_{cur_date}.csv', 'w', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(
            (
                'Артикул',
                'Ссылка'
            )
        )


    clocks_list = []

    for page in range(1, pages_count):

        with open(f'data/page_{page}.html', encoding='utf-8') as file:
            src = file.read()

        soap = BeautifulSoup(src, 'lxml')
        clocks = soap.find_all(class_="product-item__link")

        for clock in clocks:

            articul = clock.find(class_="product-item__articul").text.strip()
            clock_url = 'https://shop.casio.ru' + clock.get('href')

            clocks_list.append(
                {
                    'clock_articul': articul,
                    'clock_url': clock_url
                }
            )

            with open(f'data_{cur_date}.csv', 'a', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(
                    (
                        articul,
                        clock_url
                    )
                )

        with open(f'data_{cur_date}.json', 'a', encoding='utf-8') as file:
            json.dump(clocks_list, file, indent=4, ensure_ascii=False)

def main():
    collect_data(get_all_pages())

if __name__ == "__main__":
    main()
