"""
парсим сайт фестивалей
достаем каждый фестиваль
url = 'https://www.skiddle.com/festivals/search/'
"""

import requests, json, lxml
from bs4 import BeautifulSoup


headers = {
    'accept': '*/*',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36'
}

"""
сайт динамический, ищем в запросе перехода и в url ищем офсет или что-то похожее
параметр o
далее ищем значение параметра на последней странице - 264
так же в запросе перехода, можно перейти во вкладку предварительного просмотра,
и увидеть словарь с ключом "html" который хранит весь html код открываемой страницы
url = 'https://www.skiddle.com/festivals/search/?ajaxing=1&sort=0&fest_name=&from_date=25%20Mar%202022&to_date=&maxprice=500&o=264&bannertitle=April'
"""
festival_url_list = []

for i in range(0, 264 + 24, 24):
    url = f'https://www.skiddle.com/festivals/search/?ajaxing=1&sort=0&fest_name=&from_date=25%20Mar%202022&to_date=&maxprice=500&o={i}&bannertitle=April'
    req = requests.get(url, headers=headers)
    """
    здесь и заберем то что хранит ключ html
    """
    json_data = json.loads(req.text)
    html_res = json_data['html']
    """
    пишем в файл и смотрим что получилось
    """
    with open(f'data/index_{i}.html', 'w', encoding='utf-8') as file:
        file.write(html_res)

    with open(f'data/index_{i}.html', encoding='utf-8') as file:
        src = file.read()

    soap = BeautifulSoup(src, 'lxml')
    festivals = soap.find_all(class_="margin-top-0 margin-bottom-5 card-title")

    for festival in festivals:
        festival_url_list.append('https://www.skiddle.com' + festival.find('a').get('href'))

"""
далее летим собирать данные каждого феста
добовлять их в список
а потом запишем список в json
"""
data_festivals_list = []
n = 1

for festival_url in festival_url_list:
    print(festival_url)

    data_festival = {}

    src_fest = requests.get(festival_url, headers=headers).text
    soap = BeautifulSoup(src_fest, 'lxml')

    """
    в некоторых фестах отсутствует информация о нем
    попадись в цикле такой фест, нам прилетит ошибка
    словим ее и заигнорим фест
    """
    try:
        name_fest = soap.find(class_="margin-bottom-10 tc-white").text.strip()
        data_festival['name'] = name_fest
        date_fest = soap.find(class_="no-transform normal tc-white").text.strip()
        data_festival['date'] = date_fest

        url_location = 'https://www.skiddle.com' + soap.find('a', class_="tc-white").get('href')
        src_location = requests.get(url_location, headers=headers).text
        soap = BeautifulSoup(src_location, 'lxml')


        """
        в некоторых фестах отсутсвует контактная инфа феста
        при сборе контактных данных тоже прилетит ошибка
        словим ее и не будем добавлять контактные данные
        """
        try:
            """
            при добыче всей контактной инфы, столкнулся с проблемой
            - на разных фестах, она хранилась в разных тегах, и у нее не было общего класса для поиска
            пришлось отталкиваться от точки опоры и искать каждую инфу, по общему тегу самой инфы
            """
            content_last_contact = soap.find('h2', string='Venue contact details and info').find_next()
            """
            далее можно пройти циклом по поиску всех нужных тегов,
            а можно сделать это с каплей магии
            на всякий случай оставлю то как выглядила бы следующая строка:
            p_list = content_last_contact.find_all('p')
            items = []
            for p in p_list:
                items.append(p.text)
            """
            items = [item.text for item in content_last_contact.find_all('p')]
            """
            далее создаем словарь с контактными данными и вставляем в него все контакты из списка
            """
            contacts = {}
            for i in items:
                key, value = i.split(": ", 1)
                contacts[key] = value

            data_festival['contacts'] = contacts
            data_festivals_list.append(data_festival)
        except Exception as ex:
            print(ex)
            print('Отсутствуют контактные данные феста')
            data_festivals_list.append(data_festival)

        print(f'итерация {n} завершена!')
        n += 1
    except Exception as ex:
        print(ex)
        print('Отсутствуют данные феста')

print("все итерации завершены!")

with open('data/festivals.json', 'w', encoding='utf-8') as file:
    json.dump(data_festivals_list, file, ensure_ascii=False, indent=4)


