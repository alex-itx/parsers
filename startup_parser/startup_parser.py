"""
Парсим сайт со стартапами на их содержимое
"""
import json
import requests
from bs4 import BeautifulSoup
import os

"""
функция будет принимать url сайта и далее парсить уже по знакомому нам сценарию с небольшими отличаями,
учитывая содержимое сайта
"""
def get_data(url):

    headers = {
        'accept': '*/*',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36'
    }

    req = requests.get(url, headers=headers)
    req_text = req.text

    with open('data/page1.html', 'w', encoding='utf-8') as file:
        src = file.write(req_text)

    with open('data/page1.html', encoding='utf-8') as file:
        src = file.read()

    startups_from_json = []


    soap = BeautifulSoup(src, 'lxml')

    for page in range(1, 43):
        os.mkdir(f'data/page{page}')


        startapus = soap.find(class_="projects_list_c").find_all(class_="projects_list_b")[1:]

        n = 1
        for startap in startapus:
            startup_name =startap.find(class_="title").text
            symbols = [' ', '-', '"', "'", ',', '/', '|', '\\', ':', '*', '?', '+', '<', '>']
            for symbol in symbols:
                if symbol in startup_name:
                    startup_name = startup_name.replace(symbol, '_')

            startup_url = startap.get('href')

            req = requests.get(startup_url, headers=headers)
            req_text = req.text

            with open(f'data/page{page}/{n}_{startup_name}.html', 'w', encoding='utf-8') as file:
                file.write(req_text)

            with open(f'data/page{page}/{n}_{startup_name}.html', encoding='utf-8') as file:
                src = file.read()

            soap = BeautifulSoup(src, 'lxml')

            spans = soap.find(class_="main_d").find_all('span')[:4]

            data_startup = {
                    'startup_name': startup_name,
                    'description': spans[0].text,
                    'place': spans[1].text,
                    'industry': spans[2].text,
                    'project_stage': spans[3].text.strip()
                }

            startups_from_json.append(data_startup)


            with open(f'data/page{page}/{n}_{startup_name}.json', 'w', encoding='utf-8') as file:
                json.dump(data_startup, file, indent=4, ensure_ascii=False)

            n += 1


        """
        В моем случае так как сайт разделен на страницы с переходом по клику,
        я попросту выяснил какая страница последняя и добавил к url параметр страницы с ее номером (page)
        если бы мы брали сайт с динамически добавляющимися страницами от прокрутки, мы бы заметили,
        что при прокрутки в url странице так же в параметре page добавляется номер,
        и точно таким же методом добавляли страницу
        также изменение пагинации можно посмотреть в коде страницы во вкладке "сеть",
        при прокрутке, мы увидим как на страницу приходит запрос на изменение пагинации,
        как правило это отображается в самом низу запроса, либо в конце url запроса
        """
        req = requests.get(url + f'page/{page + 1}/', headers=headers)
        req_text = req.text

        with open(f'data/page{page + 1}.html', 'w', encoding='utf-8') as file:
            src = file.write(req_text)

        with open(f'data/page{page + 1}.html', encoding='utf-8') as file:
            src = file.read()

        soap = BeautifulSoup(src, 'lxml')

        print(f'итерация {page} - завершена!')

        if page == 42:
            with open(f'data/all_startups.json', 'w', encoding='utf-8') as file:
                json.dump(startups_from_json, file, indent=4, ensure_ascii=False)
            print('все итерации завершены!')

"""
добавляем нашу функцию в автовключение
"""
def main():
    get_data('https://ru.startup.network/startups/')


if __name__ == '__main__':
    main()
