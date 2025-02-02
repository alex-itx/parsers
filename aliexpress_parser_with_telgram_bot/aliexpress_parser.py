"""
парсим товары из алика
"""
import requests, os, json, csv, time, re
from bs4 import BeautifulSoup

# url сайта с которого надо парсить
url = 'https://aliexpress.ru/wholesale?CatId=&isTmall=n&isFreeShip=n&isFavorite=y&g=n&page=1&SearchText=%D0%B0%D0%BA%D1%81%D0%B5%D1%81%D1%83%D0%B0%D1%80%D1%8B%20%D0%B4%D0%BB%D1%8F%20%D0%B3%D0%B5%D0%B9%D0%BC%D0%BF%D0%B0%D0%B4%D0%B0%20xbox%20series'
# хейдеры сайта
headers = {
    'accept': '*/*',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36'
}

# функция сбора данных
def data_collection():
    start_time = time.time()

    session = requests.Session()
    res = session.get(url, headers=headers).text
    soup = BeautifulSoup(res, 'lxml')

    # тег который хранит последнюю странциу
    last_page_tag = soup.find(class_="ali-kit_Base__base__104pa1 ali-kit_Base__default__104pa1 ali-kit_Label__label__1n9sab ali-kit_Label__size-s__1n9sab SearchPagination_SearchPagination__label__16999")
    # обрезаем текст для получение числа посследней страницы
    last_page = int(last_page_tag.text.split(' ')[1])

    # для проверки работы программы обработаем пять страниц
    if last_page > 5:
        last_page = 5

    # конечный список продуктов
    final_list = []
    # счетчик страниц
    page_counter = 0
    # цикл по страницам
    for page in range(1, last_page + 1):
        page_counter += 1
        url_page = f'https://aliexpress.ru/wholesale?CatId=&isTmall=n&isFreeShip=n&isFavorite=y&g=n&page={page}&SearchText=%D0%B0%D0%BA%D1%81%D0%B5%D1%81%D1%83%D0%B0%D1%80%D1%8B%20%D0%B4%D0%BB%D1%8F%20%D0%B3%D0%B5%D0%B9%D0%BC%D0%BF%D0%B0%D0%B4%D0%B0%20xbox%20series'
        session = requests.Session()
        res = session.get(url_page, headers=headers).text
        soup = BeautifulSoup(res, 'lxml')


        # все карты на странице
        cards = soup.find_all(class_="SearchProductFeed_ProductSnippet__content__1yqru")


        # счетчик карточек
        cards_count = 0
        # цикл по каждой карточке на странице
        for card in cards:
            cards_count += 1
            # ссылка на карточку
            url_card = f"https://aliexpress.ru{card.find('a').get('href')}"

            # описание
            description = card.find(class_="SearchProductFeed_ProductSnippet__name__1yqru").text

            # ищем ссылку на картинку (она не лежит в разных параметрах на разных карточка, а еще она без протокола)
            images_url = card.find(class_="SearchProductFeed_Gallery__image__1ln22").get('src')
            if images_url is None:
                images_url = card.find(class_="SearchProductFeed_Gallery__image__1ln22").get('data-src')

            images_card = f'https:{images_url}'

            # ищем старую цену
            try:
                old_price = card.find(class_="snow-price_SnowPrice__secondPrice__2y0jkd").text.split()[:-1]
                old_price = ''.join(old_price).replace(',', '.')

            except Exception as ex:
                old_price = 'нет старой цены'

            # ищем цену
            price = card.find(class_="snow-price_SnowPrice__mainM__2y0jkd").text.split()[:-1]
            price = ''.join(price).replace(',', '.')

            # ищем скидку
            if old_price != 'нет старой цены':
                sale = round((float(old_price) - float(price)) / (float(old_price) / 100))
            else:
                sale = 'нет скидки'

            # наполняем конечный список
            final_list.append(
                {
                    'description': description,
                    'url': url_card,
                    'img': images_card,
                    'price': price,
                    'old_price': old_price,
                    'sale': str(sale)
                }
            )
            print(f'[INFO] обработана {cards_count} страница из {len(cards)}')

        print(f'[INFO] обработана {page_counter} страница из {last_page}')
    # пишем в json
    with open('data.json', 'w', encoding='utf-8') as file:
        json.dump(final_list, file, indent=4, ensure_ascii=False)

    return f'данные собраны, время сбора данных - {time.time() - start_time}'


def main():
    print(data_collection())


    # print(time.time() - start_time)


if __name__ == '__main__':
    main()
