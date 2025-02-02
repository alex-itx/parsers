"""
пирсим таблицы с даннными и перегоняем их в json, csv, lxls, перехватываем post запрос с сайта,
конвертируем curl в функцию
"""
import requests, csv, time
from proxies_info import ip_port, login, password
from datetime import datetime
from bs4 import BeautifulSoup
# вызываем эту функцию что бы не получать злобное предупреждения от IDE во время скачивания xlsx таблиц
requests.packages.urllib3.disable_warnings()

url = 'https://www.bls.gov/regions/midwest/data/averageenergyprices_selectedareas_table.htm'

headers = {
    'accept': '*/*',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.115 Safari/537.36'
}

proxies = {
    'https': f'http://{login}:{password}@{ip_port}'
}

def get_data():
    res = requests.get(url, headers=headers, proxies=proxies).text

    with open('index.html', 'w', encoding='utf-8') as file:
        file.write(res)

    with open('index.html', encoding='utf-8') as file:
        src = file.read()

    soup = BeautifulSoup(src, 'lxml')

    # достаем всю таблицу
    table = soup.find('table', id="ro5xgenergy")

    # список заголовков
    table_headers = ['Area']
    # достаем заголовки
    data_th = table.find('thead').find_all('tr')[-1].find_all('th')

    # добавляем загаловки в список
    for th in data_th:
        table_headers.append(th.text)

    # пишем заголовки в csv

    cur_date = datetime.now().strftime('%m_%d_%Y')
    with open(f'table_energy_{cur_date}.csv', 'w', encoding='utf-8') as file:
        writer = csv.writer(file)

        writer.writerow(
            (
                table_headers
            )
        )

    # забираем все строки данных
    data_str = table.find('tbody').find_all('tr')

    # создаем список для сбора id которые будем собирать для скачивания таблиц
    ids = []
    # бежим по строкам
    for tr in data_str:
        # забираем локацию
        area = tr.find('th').text.strip()
        # забираем ячейки строки
        data_td = tr.find_all('td')

        # создаем список с ячейками строки
        data = [area]
        # бежим по ячейкам
        for td in data_td:
            # если в ячейке ссылка - забираем ее
            if td.find('a'):
                area_data = td.find('a').get('href')
                # забираем из ссылки id и ложем его в список, он понадобиться дальше, чтобы скачивать xlsx таблицы
                id_ = area_data.split('/')[4].split('?')[0]
                ids.append(id_)
            # если текст - то забираем текст
            elif td.find('span'):
                area_data = td.find('span').text
            # если ячейка пустая, ее значение будет 'None'
            else:
                area_data = 'None'

            # добавляем ячейку в список
            data.append(area_data)

        # дозаписываем строку в csv
        with open(f'table_energy_{cur_date}.csv', 'a', encoding='utf-8') as file:
            writer = csv.writer(file)

            writer.writerow(
                (
                    data
                )
            )

    with open('ids.txt', 'w', encoding='utf-8') as file:
        for id in ids:
            file.write(f'{id}\n')

    return 'основная таблица готова'

# функция скачивания xlsx таблиц
def download_xlsx():
    """
    всё тело цикла взята из ответа расшифровки curl url при перехвате запроса на сайте в момент скачивания таблицы
    расшифровка curl осуществляется на сайте - https://curlconverter.com/
    перехват post запроса делается программой Burp Suite
    из тела удалены только cookies и импорт реквеста так как они не нужны
    """

    with open('ids.txt', encoding='utf-8') as file:
        ids = [line.strip() for line in file.readlines()]

    # бежим по каждому id в дальнейшем будем подменять id в переменной data
    for n, id_ in enumerate(ids):

        headers = {
            'Host': 'data.bls.gov',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:101.0) Gecko/20100101 Firefox/101.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://data.bls.gov',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            # Requests doesn't support trailers
            'Te': 'trailers',
            'Connection': 'close',
        }

        data = f'request_action=get_data&reformat=true&from_results_page=true&years_option=specific_years&delimiter=comma&output_type=multi&periods_option=all_periods&output_view=data&output_format=excelTable&original_output_type=default&annualAveragesRequested=false&series_id={id_}'

        response = requests.post('https://data.bls.gov/pdq/SurveyOutputServlet',  headers=headers, proxies=proxies,
                                 data=data, verify=False)

        # записываем таблицу в файл - это делаем сами
        with open(f'tables/{id_}text.xlsx', 'wb') as file:
            file.write(response.content)

        print(f'файл {n + 1} из {len(ids)} скачан')

    return 'дополнительные таблицы скачены'


def main():
    start_time = time.time()

    print(get_data())
    print(download_xlsx())

    print(f'время работы программы - {time.time() - start_time}')
if __name__ == "__main__":
    main()
