import requests
from bs4 import BeautifulSoup
import json
import time

# Базовый URL сайта
base_url = "https://stoigr.org"

# Список категорий (пример; замените на реальные категории)
categories = [
#     "hotgames-2023",
# "online-games",
# "arkady-games",
# "golovolomki",
# "gonki-games",
# "gonki-for-two-game",
# "gonki-na-motociklah",
# "russian-cars-gonki",
# "dopolneniya-games",
# "draki-games",
# "zombie-games",
# "dlya-devochek-games",
# "kids-game",
# "game-for-boys",
# "survival-game",
# "games-two",
# "russian-games",
# "dlya-slabyh-pk",
# "mechanics-games-torrent",
# "xatab-games-torrent",
# "indie-games",
# "kvest-games",
# "logic-games",
# "open-world-games",
# "sandbox-game",
# "platformer-game",
# "poisk-predmetov-games",
# "priklyucheniya-games",
# "rpg-games",
# "sborniki-games",
# "simulyatory-games",
# "sport-games",
# "strategii-games",
# "top-100-games",
# "horror-games",
# "shuter-games",
# "shitery-ot-pervogo-litsa",
# "action-games",
"erotic-game",
# "ya-ishchu-game",
    # Добавьте другие категории, которые вам нужны
]


# Функция для парсинга страниц категорий
def parse_category(category):
    current_page = 1
    game_links = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    while True:
        # Формируем URL для текущей страницы
        if current_page == 1:
            url = f"{base_url}/{category}/"  # Базовая категория для первой страницы
        else:
            url = f"{base_url}/{category}/page/{current_page}/"  # Для остальных страниц

        print(f"Парсинг страницы: {url}")

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Ошибка доступа к {url}: {e}")
            break

        soup = BeautifulSoup(response.content, 'html.parser')

        # Извлекаем ссылки на страницы игр
        page_links = soup.select('div.short-story a')
        if not page_links:  # Если на странице нет ссылок, заканчиваем
            print(f"Ссылки не найдены на странице {url}. Возможно, достигли последней страницы.")
            break

        for link in page_links:
            game_links.append(link['href'])  # Сохраняем относительные ссылки

        # Проверяем наличие навигации и кнопки "Вперед"
        navigation = soup.select_one('div.navigation')
        if navigation and navigation.find('a', string="Вперед"):
            current_page += 1  # Переходим к следующей странице
        else:
            print("Достигнута последняя страница.")
            break

    return game_links




# Функция для парсинга страницы игры
# Функция для парсинга страницы игры
# Функция для парсинга страницы игры
def parse_game_page(game_url):
    url = game_url if game_url.startswith("http") else f"{base_url}{game_url}"  # Формируем полный URL
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)  # Установите тайм-аут
        response.raise_for_status()  # Проверка на ошибки
    except requests.exceptions.RequestException as e:
        print(f"Ошибка доступа к {url}: {e}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')
    downloads = []

    # Найдите все элементы, содержащие информацию о загрузках
    download_items = soup.select('.download')
    print(f"Найдено элементов загрузки на {url}: {len(download_items)}")  # Отладочное сообщение

    for item in download_items:
        title_element = item.find('h2')
        if title_element is None:
            print(f"Заголовок не найден на странице {url}")
            continue  # Пропускаем, если заголовок не найден

        title = title_element.text.strip()  # Заголовок

        magnet_element = item.select_one('.button4')
        if magnet_element is None or 'href' not in magnet_element.attrs:
            print(f"Ссылка на торрент не найдена на странице {url}")
            continue  # Пропускаем, если ссылка не найдена

        magnet_link = magnet_element['href']  # Ссылка на торрент

        # Изменяем селектор для получения размера файла
        file_size_element = item.find('td', class_='tdname', string='Размер:')
        if file_size_element is None:
            print(f"Размер файла не найден на странице {url}")
            continue  # Пропускаем, если размер файла не найден

        # Получаем следующий элемент <td>, который содержит размер файла
        file_size = file_size_element.find_next_sibling('td').text.strip()  # Размер файла

        # Добавляем поле "uploadDate" с фиксированной датой
        upload_date = "2024-09-20T08:06:00Z"

        downloads.append({
            "title": title,
            "uris": [magnet_link],
            "uploadDate": upload_date,  # Добавлено поле
            "fileSize": file_size,
            "repackLinkSource": url  # Ссылка на страницу игры
        })

    return downloads



# Основная функция
def main():
    all_downloads = []

    for category in categories:
        game_links = parse_category(category)  # Получаем ссылки на игры
        for game_link in game_links:
            downloads = parse_game_page(game_link)  # Парсим каждую страницу игры
            if downloads:
                all_downloads.extend(downloads)
            time.sleep(1)  # Задержка между запросами, чтобы избежать блокировок

    result = {
        "name": "Stoigr | All Categories",
        "downloads": all_downloads
    }

    # Сохранение результата в JSON файл
    with open('downloads.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)

    print(f"Сохранено {len(all_downloads)} загрузок в downloads.json")  # Отладочное сообщение


if __name__ == "__main__":
    main()