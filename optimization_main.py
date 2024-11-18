import requests
from bs4 import BeautifulSoup
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

# Базовый URL сайта
base_url = "https://stoigr.org"

# Список категорий
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
"ya-ishchu-game"
]

# Максимальное количество попыток для повторного парсинга
MAX_RETRIES = 3


# Функция для получения содержимого страницы
def fetch(url, retries=0):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Ошибка доступа к {url}: {e}")
        if retries < MAX_RETRIES:
            print(f"Повторная попытка {retries + 1} для {url}")
            return fetch(url, retries=retries + 1)
        return None


# Функция для парсинга всех страниц категории
def parse_category(category):
    game_links = []
    current_page = 1

    while True:
        url = f"{base_url}/{category}/" if current_page == 1 else f"{base_url}/{category}/page/{current_page}/"
        print(f"Парсинг страницы категории {category}: {url}")
        page_content = fetch(url)
        if not page_content:
            failed_pages.append(url)
            break

        soup = BeautifulSoup(page_content, 'html.parser')
        page_links = soup.select('div.short-story a')
        if not page_links:
            break

        for link in page_links:
            game_links.append(link['href'])

        navigation = soup.select_one('div.navigation')
        if navigation and navigation.find('a', string="Вперед"):
            current_page += 1
        else:
            break

    return game_links


# Функция для парсинга страницы игры
def parse_game_page(game_url):
    url = game_url if game_url.startswith("http") else f"{base_url}{game_url}"
    page_content = fetch(url)
    if not page_content:
        failed_pages.append(url)
        return []

    soup = BeautifulSoup(page_content, 'html.parser')
    downloads = []

    download_items = soup.select('.download')
    for item in download_items:
        title_element = item.find('h2')
        if not title_element:
            continue

        magnet_element = item.select_one('.button4')
        if not magnet_element or 'href' not in magnet_element.attrs:
            continue

        file_size_element = item.find('td', class_='tdname', string='Размер:')
        if not file_size_element:
            continue

        file_size = file_size_element.find_next_sibling('td').text.strip()
        upload_date = "2024-09-20T08:06:00Z"

        downloads.append({
            "title": title_element.text.strip(),
            "uris": [magnet_element['href']],
            "uploadDate": upload_date,
            "fileSize": file_size,
            "repackLinkSource": url
        })

    return downloads


# Функция для повторного парсинга неудачных страниц
def retry_failed_pages():
    print(f"Попытка повторного парсинга {len(failed_pages)} неудачных страниц...")
    successful_downloads = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(fetch, url): url for url in failed_pages}
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                page_content = future.result()
                if page_content:
                    if "page" in url:  # Это страница категории
                        successful_downloads.extend(parse_category(url))
                    else:  # Это страница игры
                        successful_downloads.extend(parse_game_page(url))
                    failed_pages.remove(url)  # Удаляем успешные из списка
            except Exception as e:
                print(f"Ошибка при повторном парсинге {url}: {e}")

    return successful_downloads


# Основная функция для многопоточного парсинга
failed_pages = []  # Глобальный список для хранения неудачных страниц

def main():
    all_downloads = []

    # Парсинг категорий в 4 потока
    with ThreadPoolExecutor(max_workers=4) as category_executor:
        category_futures = {category_executor.submit(parse_category, category): category for category in categories}

        for future in as_completed(category_futures):
            category = category_futures[future]
            try:
                game_links = future.result()
                print(f"Получено {len(game_links)} ссылок из категории: {category}")

                # Парсинг страниц игр в потоках
                with ThreadPoolExecutor(max_workers=10) as game_executor:
                    game_futures = {game_executor.submit(parse_game_page, link): link for link in game_links}

                    for game_future in as_completed(game_futures):
                        try:
                            downloads = game_future.result()
                            if downloads:
                                all_downloads.extend(downloads)
                        except Exception as e:
                            print(f"Ошибка при парсинге игры: {e}")

            except Exception as e:
                print(f"Ошибка при парсинге категории {category}: {e}")

    # Повторный парсинг неудачных страниц
    retry_results = retry_failed_pages()
    all_downloads.extend(retry_results)

    result = {
        "name": "Stoigr | All Categories",
        "downloads": all_downloads
    }

    # Сохранение результата в JSON файл
    with open('downloads_optimized.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)

    print(f"Сохранено {len(all_downloads)} загрузок в downloads_optimized.json")


if __name__ == "__main__":
    main()
