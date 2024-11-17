import requests
from bs4 import BeautifulSoup
import json

# Базовый URL сайта
base_url = "https://stoigr.org"


# Функция для парсинга категорий игр
def parse_categories():
    url = base_url  # Начальная страница
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
    categories = []

    # Находим все категории в меню
    menu_items = soup.select('.menu ul li a')

    for item in menu_items:
        category_name = item.text.strip()  # Название категории
        category_link = item['href']  # Ссылка на категорию

        categories.append({
            "name": category_name,
            "link": category_link
        })

    return categories


# Основная функция
def main():
    categories = parse_categories()  # Получаем категории
    if categories:
        # Сохранение результата в JSON файл
        with open('categories.json', 'w', encoding='utf-8') as f:
            json.dump(categories, f, ensure_ascii=False, indent=4)

        print(f"Сохранено {len(categories)} категорий в categories.json")  # Отладочное сообщение


if __name__ == "__main__":
    main()