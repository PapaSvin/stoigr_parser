import requests
from bs4 import BeautifulSoup
import json
import time

# Базовый URL сайта
base_url = "https://stoigr.org"

# Список категорий (пример; замените на реальные категории)
categories = [
    "hotgames-2023",
"online-games",
"arkady-games",
"golovolomki",
"gonki-games",
"gonki-for-two-game",
"gonki-na-motociklah",
"russian-cars-gonki",
"dopolneniya-games",
"draki-games",
"zombie-games",
"dlya-devochek-games",
"kids-game",
"game-for-boys",
"survival-game",
"games-two",
"russian-games",
"dlya-slabyh-pk",
"mechanics-games-torrent",
"xatab-games-torrent",
"indie-games",
"kvest-games",
"logic-games",
"open-world-games",
"sandbox-game",
"platformer-game",
"poisk-predmetov-games",
"priklyucheniya-games",
"rpg-games",
"sborniki-games",
"simulyatory-games",
"sport-games",
"strategii-games",
"top-100-games",
"horror-games",
"shuter-games",
"shitery-ot-pervogo-litsa",
"action-games",
"erotic-game",
"ya-ishchu-game",
    # Добавьте другие категории, которые вам нужны
]


# Функция для парсинга страниц категорий
def parse_category(category):
    url = f"{base_url}/{category}/"
    headers = {
        'User -Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)  # Установите тайм-аут
        response.raise_for_status()  # Проверка на ошибки
    except requests.exceptions.RequestException as e:
        print(f"Ошибка доступа к {url}: {e}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    game_links = []

    # Извлечение ссылок на страницы игр
    for link in soup.select('div.short-story a'):
        game_links.append(link['href'])  # Сохраняем относительные ссылки

    return game_links


# Функция для парсинга страницы игры
def parse_game_page(game_url):
    url = game_url if game_url.startswith("http") else f"{base_url}{game_url}"  # Формируем полный URL
    headers = {
        'User -Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
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

        file_size_element = item.select_one('.tdzhach')
        if file_size_element is None:
            print(f"Размер файла не найден на странице {url}")
            continue  # Пропускаем, если размер файла не найден

        file_size = file_size_element.find_next_sibling('td').text.strip()  # Размер файла

        status_element = item.select_one('#tdstatus')
        status = status_element.text.strip() if status_element else "Не указано"  # Статус

        downloads.append({
            "title": title,
            "uris": [magnet_link],
            "fileSize": file_size,
            "status": status,
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