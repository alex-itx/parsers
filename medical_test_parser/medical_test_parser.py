"""
парсим сайт анализов, парсим информацию о каждом анализе
url = 'https://www.lifetime.plus/'
"""

import requests, os, csv, json
from datetime import datetime
from proxies_info import login, password, ip_port

# api сайта
url = 'https://www.lifetime.plus/api/analysis2'

proxies = {
    'https': f'http://{login}:{password}@{ip_port}'
}

# текущая дата для имени файла
t_date = datetime.now().strftime('%d_%m_%Y')


def collect_data():
    """
    функция сбора данных с api сайта

    :return: сообщение об успешном завершение функции
    """

    # запрос на сайт
    res = requests.get(url, proxies=proxies)

    # список категорий
    categories = res.json()['categories']

    # конечный список
    result_list = []

    # цикл по каждой категории
    for category in categories:
        # имя категории
        category_name = category['name']

        # список тестов
        tests = category['items']
        # цикл по каждому анализу из категории
        for test in tests:
            # название теста
            test_name = test['name'].strip()
            # цена
            test_price = test['price']
            # описание
            test_description = test['description'].strip().replace('\n', ' ')
            # количество дней готовности теста
            test_period = test['days']
            # биоматериал
            test_biomaterial = test['biomaterial']

            # наполняем конечный список
            result_list.append(
                [category_name, test_name, test_price, test_description, test_period, test_biomaterial]
            )

    # сохраняем данные в json
    with open(f'result_{t_date}.csv', 'w', encoding='utf-8') as file:
        writer = csv.writer(file)

        writer.writerow(
            (
                'Категория',
                'Название теста',
                'Цена теста',
                'Описание теста',
                'Готовность дней',
                'Биоматериал'
            )
        )

        # writerows() - принимает список, где каждый элемент должен быть списком, который будет строкой в файле,
        # а каждый элемент вложенного списка будет элементом строки
        writer.writerows(
            (
                result_list
            )
        )

    return 'данные собраны!'


def main():
    collect_data()


if __name__ == '__main__':
    main()
