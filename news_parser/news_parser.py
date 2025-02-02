"""
парсим и копируем новостной сайт
"""

import requests, json, time
from bs4 import BeautifulSoup

url = 'https://hitech-news.ru/category/news/page/1'
headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
}

# функция сбора url
def get_news_urls():
    start_time = time.time()

    session = requests.Session()
    response = session.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "lxml")

    # последняя страница
    last_page = soup.find('a', class_='last').text

    # конечный список url карточек на всех страницах
    news_card_urls = []

    counter_page = 0
    # цикл по каждой странице сайта
    for page in range(1, int(last_page) + 1):
        counter_page += 1

        url_page = f'https://hitech-news.ru/category/news/page/{page}'

        response = session.get(url_page, headers=headers)
        soup = BeautifulSoup(response.text, "lxml")

        # новостные карточки на странице
        cards = soup.find_all(class_="td-block-span6")

        # цикл по каждой карточке
        for card in cards:
            card_url = card.find('a').get('href')
            news_card_urls.append(card_url)

        print(f'страница {counter_page} из {last_page} обработана')

    # записываем конечный список в файл
    with open('cards.txt', 'w', encoding='utf-8') as file:
        for url_card in news_card_urls:
            file.write(f'{url_card}\n')

    print(f"время сбора url - {time.time() - start_time}")
    return 'urls собраны!'

# функция по сбору данных
def get_data():
    start_time = time.time()

    with open('cards.txt', encoding='utf-8') as file:
        urls_list = [line.strip() for line in file.readlines()]

    session = requests.Session()

    # конечный список
    result_list = []

    counter = 0
    # цикл по каждой новости
    for url_news in urls_list:
        counter += 1

        res = session.get(url_news, headers=headers).text
        soup = BeautifulSoup(res, 'lxml')

        # достаем заголовок
        title = soup.find('h1').text.strip()

        # дату публикации
        date = soup.find(class_="entry-date updated td-module-date").text

        # картинку новости
        try:
            image = soup.find(class_="td-modal-image").get('src')
        except Exception as _ex:
            image = 'без картинки'

        # текст
        text = soup.find(class_="td-post-content tagdiv-type").text.strip()[:-7].strip()

        result_list.append(
            {
                'title': title,
                'date': date,
                'image': image,
                'text': text,
            }
        )

        print(f'обработана {counter} страница из {len(urls_list)}')

    with open('result.json', 'w', encoding='utf-8') as file:
        json.dump(result_list, file, indent=4, ensure_ascii=False)

    print(f"время сбора данных - {time.time() - start_time}")
    return 'данные собраны!'

def main():
    start_time = time.time()

    print(get_news_urls())
    print(get_data())

    print(f"время работы скрипта - {time.time() - start_time}")

if __name__ == '__main__':
    main()
