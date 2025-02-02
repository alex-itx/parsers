'''
Парсер лендингов
'''

import requests, time, os, json

start_time = time.time()
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36'
}

# конечный список данных
result_list = []
# функция по сбору данных
def get_data_file(headers):
    start_time = time.time()

    # счетчик страниц
    count = 1

    while True:
        # ссылка с сайта на json страницу
        url = f'https://www.landingfolio.com/api/inspiration?page={count}'
        req = requests.get(url, headers=headers)
        res = req.json()

        # если json пустой - закончить цикл
        if len(res) == 0:
            break

        # цикл по карточкам-лендингам
        for item in res:
            # имя лендинга
            title = item['title']
            # ссылка на лендинг
            url = item['url']
            # категории лендинга
            categories = []
            for category in item['categories']:
                categories.append(category)
            if len(categories) == 0:
                categories = "uncategorized"
            # скриншоты лендингов
            images = []
            for img in item['screenshots']:
                images.append({'type': img["title"],
                               'url': f'https://landingfoliocom.imgix.net/{img["images"]["desktop"]}'})

            result_list.append(
                {
                    'title': title,
                    'url': url,
                    'categories': categories,
                    'images': images
                }
            )

        print(f'страница {count} готова')
        count += 1

    with open('result_list.json', 'w', encoding='utf-8') as file:
        json.dump(result_list, file, indent=4, ensure_ascii=False)

    print(f'время сбора данных - {time.time() - start_time}')


# функция скачивания всех скриншотов, принимает путь к файлу с данными
def download_imgs(file_path):
    start_time = time.time()
    # если путь указан верный, забираем весь список
    try:
        with open(file_path) as file:
            src = json.load(file)

    # если нет возвращает ошибку и сообщение
    except Exception as _ex:
        print(_ex)
        return "Проверь путь к файлу"

    # общее количество карточек
    items_len = len(src)
    # счетчик карточек
    count = 1
    for item in src:
        # имя для названия директории
        name = item['title']
        # список скриншотов карточки
        imgs = item['images']

        # если если такой директории нет
        if not os.path.exists(f'data/{name}'):
            # то создаем ее
            os.mkdir(f'data/{name}')

        # перебираем скриншоты
        for img in imgs:
            # реквестим картинку
            req = requests.get(img['url'])
            # сохраняем ее в файл
            with open(f'data/{name}/{img["type"]}.png', 'wb') as file:
                file.write(req.content)
        print(f'скачено {count} из {items_len} карточек')
        count += 1

    print(f'время загрузки картинок - {time.time() - start_time}')



def main():
    get_data_file(headers)

    if not os.path.exists('data'):
        os.mkdir('data')

    download_imgs('result_list.json')

    print(f'общее время работы программы - {time.time() - start_time}')


if __name__ == '__main__':
    main()
