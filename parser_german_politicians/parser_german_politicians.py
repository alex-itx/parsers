"""
парсим контакты немецких политиков с сайта - https://www.bundestag.de/en/members
"""

import requests, os, json
from bs4 import BeautifulSoup

"""
содержимое страницы изменяется при нажатие на кнопку перемещения слайда
ссылка на каждого политика хранится в виде карточек на слайде
всего двенадцать карточек на одном слайде
при перемещение слайда, не происходит переход на другую страницу, а просто подгружаются новые карточки на месте старых
открываем панель разработчика, в ней открываем вкладку "сеть", смотрим что происходит при перемещение слайда
видим что на сайт поступает гет запрос который хранит в себе ссылку -
https://www.bundestag.de/ajax/filterlist/en/members/863330-863330?limit=20&noFilterSet=true&offset=12
в ссылке хранит в себе 20 карточек
в самой же ссылке есть параметр - limit=20, который обозначает лимит карточек на странице
так же видим параметр - set=12 который значит - после какой карточки показывать первую карточку,
то-есть если мы изменим его на ноль, первая карточка на странице будет та же что и первая карточка на изначальной ссылке,
правда немного в другом порядке - на слайде начальной странице карты расположены в две строки по шесть штук,
здесь порядок такой - первые 4 с первой строки, первые 4 со второй строки, следующие 4 с первой строки и т.д.
при открывание панели разработчика слайд основной странице сужается,
оставляя 8 карточек на странице и появляется счетчик слайдов,
где последней страницей является 93
92 * 8 = 736, значит на сайте более 736 карточек
методом тыка узнаем сколько запросов мы будем делать изменяя метод set в ссылке
пробуем 740 и узнаем что карточек на странице не более 740
нам достаточно и этой информации но для интереса узнаем сколько всего карточек
пробуем 720 и нам открывается страница на которой 17 карточек
и того карточек на странице 737
пройдемся по всем ссылка хранящие по 20 карточек через цикл, изменяя параметр set и заберем url всех карточек
"""
url_cards = []

for cards in range(0, 740, 20):
    req = requests.get(f'https://www.bundestag.de/ajax/filterlist/en/members/863330-863330?limit=20&noFilterSet=true&offset={cards}')
    """
    достаем html содержимое страници методом content функции get - это почти тоже самое что и метод text
    только формат отображения слегка другой, в content перенос строки отображается символом переноса
    то-есть не закодирован
    """
    result = req.content

    soap = BeautifulSoup(result, 'lxml')
    cards_in_slide = soap.find_all(class_="bt-open-in-overlay")

    for card in cards_in_slide:
        url_cards.append(card.get('href'))

with open('person_url_list.txt', 'a') as file:
    for line in url_cards:
        file.write(f'{line}\n')


with open('person_url_list.txt') as file:
    url_cards = []
    for line in file.readlines():
        url_cards.append(line.strip())
    """
    есть более простой способ сделать тоже самое:
    url_cards = [line.strip() for line in file.readlines()]
    """


"""
дальше парсим нужную нам информацию по каждому политику
и записываем все в json файл
"""

persons_list = []

# count = 1
for url_card in url_cards:
    q = requests.get(url_card)
    res = q.content

    soap = BeautifulSoup(res, 'lxml')
    name_and_company = soap.find(class_="col-xs-8 col-md-9 bt-biografie-name").find('h3').text.strip().split(',')
    name = name_and_company[0]
    company = name_and_company[1].strip()

    soc_networks = []
    tags_soc_nets = soap.find_all(class_="bt-link-extern")
    for tag in tags_soc_nets:
        soc_networks.append(tag.get('href'))

    person = {
        'name': name,
        'company': company,
        'social_networks': soc_networks
    }

    persons_list.append(person)

    # print(f'#{count} is done!')
    # count += 1

with open('persons_list.json', 'w', encoding='utf-8') as file:
    json.dump(persons_list, file, ensure_ascii=False, indent=4)
