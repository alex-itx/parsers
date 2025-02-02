"""
парсим данные отелей с сайта туристических туров

на сайте мы видим карточки разных отелей, инфу о них нам и нужно спарсить
в панели разработчика мы видим теги каждой карточки,
но при программном поиске данных тегов мы их не находим
если просмотреть текст гет запроса мы увидим что данных тегов так же нет в html коде запроса
"""
import time

import requests, time
from bs4 import BeautifulSoup
from selenium import webdriver

url = 'https://tury.ru/hotel/most_luxe.php'

def get_data(url):
    """
    и так попробуем найти теги привычным способом и сохраним текст html
    что бы посмотреть найдем ли мы чего там
    файл html будет без переносов строки, что бы посмотреть его в привычном виде можно воспользоваться
    Ctrl + Alt + Shift + L
    """
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        # 'accept-encoding': 'gzip, deflate, br', какого то хера с ним не работает
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'cache-control': 'max-age=0',
        'Connection': 'keep-alive',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36'
            }

    req = requests.get(url)
    res = req.text

    with open('hotel_luxe.html', 'w', encoding='utf-8') as file:
        file.write(res)
        """
        блок в котором должны быть записаны все карточки отелей пустой
        <div id="hc_most_results"><img src="/im/loading16.gif" style="margin:32px;"></div>
        """

    # soap = BeautifulSoup(res, 'lxml')
    # hotels = soap.find_all(class_="hotel_card_dv")
    # # выдаёт пустой список
    # print(hotels)

    """
    Итак все написанное выше не работает т.к. мы не можем получить наши карточки
    что делать?
    снова лезем на вкладку "сеть" и ищем другие гет запросы
    узнаем что в одном из запросов есть интересный url:
    https://api.rsrv.me/hc.php?a=hc&most_id=1317&l=ru&sort=most&hotel_link=/hotel/id/%HOTEL_ID%&r=1660324714
    переходим и у нас появляется страница с нашими карточками
    такое бывает довольно часто и ответы подобных запросов в основном приходят в json формате
    хотя в нашем случае почему то ответом является html код подгружаемой странице
    так-же если покопаться в полученном ранее html коде можно найти тег перед искомым тегом,
    который хранит в себе функцию, которая вызывает подгрузку некого url на страницу
    это тот самый url  с карточками 
    Итак эту ссылку мы и будем парсить
    в ней мы видим множество непонятных параметров
    отличный совет по работе с ссылками:
    попробуйте удалить какой нибудь параметр и проверить измениться ли страница на отображение
    если не измениться, то лучше работать с ссылкой без этих параметров,
    так как этими параметрами могут быть какие-то ключи или токены
    чтобы не искать и парсить лишнее лучше просто обрезать ссылку
    https://api.rsrv.me/hc.php?a=hc&most_id=1317&l=ru&sort=most
    """
    url = 'https://api.rsrv.me/hc.php?a=hc&most_id=1317&l=ru&sort=most'
    req_hotels = requests.get(url, headers=headers)
    res_hotels = req_hotels.text

    soap = BeautifulSoup(res_hotels, 'lxml')
    hotels = soap.find_all(class_="hotel_card_dv")

    """
    достанем все ссылки и убедимся что все работает
    """
    for hotel in hotels:
        url_hotel = hotel.find('a').get('href')
        # print(url_hotel) - все работает

"""
и так мы увидели привычный нам способ парсинга
но bs4 далеко не единственная библиотека для парсинга
есть еще одна не менее мощная библиотека для этого
selenium
давайте установим ее и выполним нашу задачу при помощи нее
для работы на с силениумом нам так же понадобиться поставить драйвер силениума в папку с файлом программы
вот ссылки на скачку драйвера
Firefox driver:
https://github.com/mozilla/geckodriver/releases
Chrome driver:
https://chromedriver.storage.googleapis.com/index.html
после распаковки драйвера в папку его нужно импортировать из селениума
from selenium import webdriver
поехали писать функцию для работы с селениумом
"""
def get_data_selenium_method(url):

    # # создаем объект опции
    # options = webdriver.FirefoxOptions()
    # # назначаем драйверу юзер агент user_agent
    # options.set_preference("general.useragent.override", 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36')
    #
    # # пишем блок try/except - в try будем забирать данные отелей, а в except ловить ошибки,
    # finally - для завершения работы драйвера
    # try:
    #     # создаем объект драйвера
    #     driver = webdriver.Firefox(
    #         # первым аргументом будет путь к драйверу
    #         executable_path='geckodriver.exe',
    #         # вторым наши опции
    #         options=options
    #     )
    #
    #     # отправляем браузер по ссылке
    #     driver.get(url=url)
    #     #  ставим паузу что-бы страница успела прогрузиться
    #     time.sleep(5)
    #
    #     # сохраним страницу что-бы потом ее распарсить
    #     with open('index_selenium.html', 'w', encoding='utf-8') as file:
    #         # метод page_sourse для записи
    #         file.write(driver.page_source)
    #
    # except Exception as ex:
    #     print(ex)
    # finally:
    #     # закрываем и выходим из драйвера
    #     driver.close()
    #     driver.quit()

    # открываем файл что бы сохронить текст в переменную и далее парсим отэли как до этого
    with open('index_selenium.html', encoding='utf-8') as file:
        src = file.read()

    soap = BeautifulSoup(src, 'lxml')
    hotels = soap.find_all(class_="hotel_card_dv")

    for hotel in hotels:
        url_hotel = hotel.find('a').get('href')
        print('https://tury.ru/' + url_hotel) # - все работает




def main():
    # get_data(url)
    get_data_selenium_method(url)

if __name__ == "__main__":
    main()
