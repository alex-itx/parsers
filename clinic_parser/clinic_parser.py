"""
парсим медицинские клиники на сайте - 'https://spb.zoon.ru/medical/
"""

import json, csv, time, requests, os, re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
# импортируем объект цепочки
from selenium.webdriver.common.action_chains import ActionChains
# импортируем метод By для поиска тегов
from selenium.webdriver.common.by import By
# импорт функции - чистки url
from urllib.parse import unquote

headers = {
    'accept': '*/*',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36'
}

def get_source_html(url):
    start_time = time.time()

    service = Service('C:\Python\Обучение\python today\selenium\googledriver\chromedriver.exe')
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()

    try:
        driver.get(url=url)
        time.sleep(3)

        # скролим страницу пока не найдем последний элемент
        while True:
            """
            ищем класс и сохраняем его в переменную, что-бы потом переместиться к нему - тем самым запустить скролл
            класс ищется в селениуме через метод find_element(), который принимает:
            параметр by= - который определяет что мы ищем. Запись идет через By.то_что_ищем, а потом ключевое слово,
            так как мы ищем по классу - ключевое слово CLASS_NAME
            что-бы пользоваться данным методом(By.), нужно его импортировать
            параметр value= принимает имя аргумента который мы ищем (в данном случае - имя класса)
            """
            find_more_element = driver.find_element(by=By.CLASS_NAME, value="catalog-button-showMore")

            """
            здесь используется метод find_elements = который возвращает список элементов
            искомый элемент есть на странице только в том случае если она не проскролена до конца
            и когда страница проскролится список будет пустым и блок не сработает
            """
            if driver.find_elements(by=By.CLASS_NAME, value='js-next-page'):
                """
                что-бы переместиться к элементу нужно использовать ActionChains - цепочка действий
                в нашем случае действие будет одно - перемещение к элементу
                для этого сначала нужно создать объект цепочки ActionChains() которая принимает драйвер
                но объект цепочки нужно импортировать

                """
                actions = ActionChains(driver)
                """
                для самого перехода нужно вызвать метод - move_to_element() (перевод - перейти к элементу),
                который принимает тег к которому надо перейти - мы сохранили его вначале цикла
                и в конце используем метод perform() - который вызывает событие (перевод - выполнить)
                """
                actions.move_to_element(find_more_element).perform()
                # пауза как и везде в работе селениума - что бы успеть все прогрузить
                time.sleep(3)

            # если сайт проскролен - сохраняем его содержимое и останавливаем цикл
            else:
                with open('source-page.html', 'w', encoding='utf-8') as file:
                    # метод page_source - позволяет сохранять контент объекта браузера
                    file.write(driver.page_source)

                break

    except Exception as _ex:
        print(_ex)
    finally:
        driver.close()
        driver.quit()
    print(f'Время работы селениума {time.time() - start_time}')

def get_urls(file_path):
    start_time = time.time()

    with open(file_path, encoding='utf-8') as file:
        src = file.read()

    soup = BeautifulSoup(src, 'lxml')
    # на странице 2 типа карточек поэтому пользуемся регуляркой
    # re.compile() - проверяет две(может и больше) строки разделенные знаком |
    cards_list = soup.find_all(class_=re.compile("minicard-item js-results-item|minicard-item js-results-item _decorated"))

    urls = []
    for url in cards_list:
        urls.append(url.find('a').get('href'))

    with open('urls.txt', 'w', encoding='utf-8') as file:
        for url in urls:
            file.write(f'{url}\n')

    print(f'Время сбора ссылок {time.time() - start_time}')

def get_data(file_path):
    start_time = time.time()

    with open(file_path, encoding='utf-8') as file:
        url_list = [url.strip() for url in file.readlines()]

    # конечный список данных
    result_list = []
    counter = 0
    for url in url_list:
        counter += 1

        res = requests.get(url, headers=headers).text
        soup = BeautifulSoup(res, 'lxml')

        # достаем название клиники
        try:
            name = soup.find('h1', class_="service-page-header--text z-text--montserrat m0").text.split()
            name = ' '.join(name)
        except Exception as _ex:
            name = 'Без названия'

        # достаем телефон
        try:
            phone = soup.find('a', class_="tel-phone js-phone-number").get('href').split(':')[1].strip()
        except Exception as _ex:
            phone = 'Без номера'

        # адрес
        try:
            address = soup.find('address', class_="iblock").text.split()
            address = ' '.join(address)
        except Exception as _ex:
            address = 'Без без адреса'

        # сайт
        try:
            site = soup.find('div', class_="service-website-value").find('a').get('href').strip()
        except Exception as _ex:
            site = 'Без сайта'

        # список соцсетей
        try:
            social_networks = soup.find('div', class_="z-text--13 service-description-social-list").find_all('a', class_="service-description-social-btn js-service-social")
            social_networks_url = [s_n.get('href') for s_n in social_networks]
            # мы получили список соцсетей, но url "грязные", создаем список чистых
            social_networks_nice_url = []
            # будем чистить каждый url и добавлять в список чистых
            for s_n in social_networks_url:
                # получаем чистый url функцией unquote(), предворитьльно импортируя ее, функция принимает url
                # получаем чистый url, но ссылка на страницу не прямая, а через сайт клиник
                # поэтому смотрим на ссылку, находим где ее обрезать, и обрезаем сплитами, а потом забираем нужную часть из списка
                social_networks_nice_url.append(unquote(s_n).split('to=')[1].split('&')[0])
        except Exception as _ex:
            social_networks_nice_url = 'Без соцсетей'


        # добавляем данные в конечный список
        result_list.append(
            {
                'name': name,
                'phone': phone,
                'address': address,
                'site': site,
                'social_networks': social_networks_nice_url
            }
        )
        print(f'[INFO] страница {counter} из {len(url_list)} завершена')

    # сохраняем конечные данные
    with open('data.json', 'w', encoding='utf-8') as file:
        json.dump(result_list, file, indent=4, ensure_ascii=False)


    print(f'Время сбора данных {time.time() - start_time}')

def main():
    start_time = time.time()
    get_source_html('https://spb.zoon.ru/medical/')
    get_urls('source-page.html')
    get_data('urls.txt')

    print(f'Время работы скрипта {time.time() - start_time}')

if __name__ == '__main__':
    main()
