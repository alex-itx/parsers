"""
парсим сайт с информацией о калорийности пищи
"""
import random
from time import sleep

import requests
from bs4 import BeautifulSoup
import json
import csv

# """
# сохраняем адрес сайта
# """
# url = 'https://health-diet.ru/table_calorie/?utm_source=leftMenu&utm_medium=table_calorie'
#
# """
# сохраняем значение хейдеров Accept и User-Agent, что бы потом добавить эти хейдеры в гет запрос
# это делается для того что бы создать хоть какуюто видимость что запрос делает не бот а реальный юзер,
# т.к. многие сайты не любят когда их парсят боты
# """
headers = {
    'Accept': '*/*',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36'
}

# """
# делаем запрос на сайт
# """
# res = requests.get(url, headers=headers)
# # print(res.text)
#
# """
# сохраняем текст в переменную и записываем его в файл
# текст лучше всегда записывать в файл,
#  т.к. от большого колличества запрософ сайт может нас заблочить или слететь,
# а с сохраненным файлом мы сможем работать дальше
# """
# src = res.text
#
# with open('lesson2.html', 'w', encoding="utf-8-sig") as file:
#     file.write(src)

# """
# мы записали код в файл и теперь нам не нужно постоянно делать запрос,
# а так как код сохранен, мы можем закоментировать все написанное выше,
# снова открыть файл на чтение и сохранить текст в переменную
# """
# with open('lesson2.html', encoding="utf-8-sig") as file:
#     src = file.read()
#
# """
# создаем парсер супа
# """
# soap = BeautifulSoup(src, 'lxml')
#
# """
# теперь ищем на сайте то что нужно спарсить
# а спарсить нам нужно кучу ссылок на продукты из разной категории
# для этого мы ищем на сайте общее значение параметра или имя тега,
# которая объединяет все наши ссылки и дальше парсим по этому параметру
# """
# all_prodduct = soap.find_all(class_="mzr-tc-group-item-href")
#
# """
# напарсили все элементы и теперь нужно все это как то красиво упаковать
# создадим словарь где ключами будут имена категорий (текст тега)
# а значением ссылка на категорю (параметр href)
# важно знать что в href храниться не вся ссылка, а ее продолжения с места откуда мы ее видим на сайте,
# это значит что для получения полной ссылки нам надо будет дописать начало ссылки к окончанию
# """
# product_dict = {}
# for item in all_prodduct:
#     text = item.text
#     url = 'https://health-diet.ru' + item['href']
#     product_dict[text] = url
#
# """
# теперь записываем полученные данные в json формат
# это во первых время на поиск сэканомит
# а во вторых, все записываем что бы не потерять!!!!!!!
# для записи в json надо импортоировать библиотеку json
# аттрибут indent в функции dump() отвечает за отступы,
# 4 - это значит 4 отступа (пробела) вначале.
# атрибут ensure_ascii отвечает за экранирование переносов строки,
# False - это значит не экранировать.
# """
# with open('category.json', 'w', encoding='utf-8-sig') as file:
#     json.dump(product_dict, file, indent=4, ensure_ascii=False)

"""
снова коментим вес код так как его результат записан,
открываем файл по новой и еще раз записываем наш словарь
"""
with open('category.json', encoding='utf-8-sig') as file:
    all_categories = json.load(file)

"""
посчитаем количество итераций, что бы потом выводить сколько их осталось,
и сразу выведем их количество
(это для красоты)
"""
count_iter = int(len(all_categories)) - 1
print(count_iter)

"""
заведем счетчик чтобы нумеровать файлы для удобства их нахождения
"""
counter = 0

"""
А теперь будем создавать свою таблицу каждой категории в формате csv
"""
for name, href in all_categories.items():
    """
    для начала давайте поменяем в имени все пробелы и ненужные нам символы на нижний слеш "_" для удобочитаемости
    """
    rep = [" ", "-", "'", ","]
    for el in rep:
        if el in name:
            name = name.replace(el, "_")
    """
    теперь делаем запрос на каждую категорию, использую url категории и уже написанными ранее хейдерами
    далее сохраним html текст страницы и запишим его в файл
    по итогу файлов будет много поэтому создадим отдельную папку для них "categories"
    """
    req = requests.get(href, headers=headers)
    src = req.text

    with open(f'categories/{counter}_{name}.html', 'w', encoding='utf-8-sig') as file:
        file.write(src)

    """
    записали, теперь все по новой
    открываем файл, созраняем код в переменную, создаем парсер супа, и ищем то что нужно спарсить на сайте
    а спарсить нам нужно таблицу со всеми блюдами и их энергитической ценностью
    """
    with open(f'categories/{counter}_{name}.html', encoding='utf-8-sig') as file:
        src = file.read()

    soap = BeautifulSoup(src, 'lxml')

    """
    проверим есть ли в данной категории таблица или эта категория пуста
    я заранее знал что в одной из категорий нет таблицы,
    поэтому нашел одну из пустых страниц,
    и в ней висит сообщение, что страница пуста
    находим код данного сообщения
    и по его присутствию проверяем есть ли в ссылке таблица или нет,
    если нет переходим к следующей итерации и файл csv не создаем
    """
    mb_error = soap.find(class_='uk-alert-danger')
    if mb_error is not None:
        continue

    table = soap.find(class_="mzr-tc-group-table").find('tr').find_all('th')
    """
    извлекаем элементы которые нашли
    так как это элементы не меняющегося списка мы можем обратиться к ним по индексам
    """
    product = table[0].text
    calories = table[1].text
    proteins = table[2].text
    fats = table[3].text
    carbohydrates = table[4].text

    """
    теперь нам нужно записать нашу таблицу
    так как это таблица нужно записать csv формате
    импортируем csv
    """
    with open(f'categories/{counter}_{name}.csv', 'w', encoding='utf-8') as file:
        """
        сздаем писатель
        """
        writer = csv.writer(file)
        """
        записываем поэлементно в строку каждый элемент методо writerow()
        метод принимает лишь один аргумент, а у нас их пять,
        для этого можно поместить все элементы в список или кортеж и передать массив
        """
        writer.writerow([
            product,
            calories,
            proteins,
            fats,
            carbohydrates
        ])

    """
    далее собираем на сайте все теги с блюдами и дозаписываем их в нашу таблицу
    """
    table = soap.find(class_="mzr-tc-group-table").find('tbody').find_all('tr')

    """
    запишем файл категории так же и в json формат, чтобы красотетски все отображать
    """
    categories_json = []

    """
    собрали теги с блюдами, теперь ищем в  них все нужные элементы и дозаписываем в таблицу
    """
    for el in table:
        tds = el.find_all('td')

        title = tds[0].text.strip()
        calories = tds[1].text
        proteins = tds[2].text
        fats = tds[3].text
        carbohydrates = tds[4].text

        """
        добавим полученные элементы и в json
        """
        categories_json.append(
            {
                'title': title,
                'calories': calories,
                'proteins': proteins,
                'fats': fats,
                'carbohydrates': carbohydrates,
            }
        )

        with open(f'categories/{counter}_{name}.csv', 'a', encoding='utf-8') as file:
            writer = csv.writer(file)

            writer.writerow([
                title,
                calories,
                proteins,
                fats,
                carbohydrates
            ])
    """
    увеличиваем счетчик чтобы пронумеровать следующие файлы
    """
    counter += 1

    """
    сохраним файлы и в json
    """
    with open(f'categories/{counter}_{name}.json', 'a', encoding='utf-8') as file:
        json.dump(categories_json, file, indent=4, ensure_ascii=False)
    """
    Наводим марафет:
    выводим сообщение какая итерация выполнена и сколько еще осталось,
    ну красотень же?!
    """
    count_iter -= 1
    print(f'итеррация {counter}. {name} записан...')
    if count_iter == 0:
        print('работа закончена')
        break
    print(f'осталось {count_iter} итерраций...')

