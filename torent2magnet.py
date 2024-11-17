import json
import requests
import bencodepy
import hashlib
import os


# Функция для загрузки .torrent файла
def download_torrent(torrent_url, save_path):
    try:
        response = requests.get(torrent_url, timeout=10)
        response.raise_for_status()
        with open(save_path, 'wb') as f:
            f.write(response.content)
        return save_path
    except Exception as e:
        print(f"Ошибка загрузки {torrent_url}: {e}")
        return None


# Функция для преобразования .torrent файла в magnet-ссылку
def torrent_to_magnet(file_path):
    try:
        with open(file_path, 'rb') as f:
            torrent_data = bencodepy.decode(f.read())

        info = torrent_data[b'info']
        info_hash = hashlib.sha1(bencodepy.encode(info)).hexdigest()
        magnet_link = f"magnet:?xt=urn:btih:{info_hash}"

        # Добавляем имя раздачи
        if b'name' in info:
            name = info[b'name'].decode('utf-8')
            magnet_link += f"&dn={name}"

        # Добавляем трекеры
        if b'announce-list' in torrent_data:
            trackers = torrent_data[b'announce-list']
            for tracker_group in trackers:
                for tracker in tracker_group:
                    magnet_link += f"&tr={tracker.decode('utf-8')}"
        elif b'announce' in torrent_data:
            tracker = torrent_data[b'announce'].decode('utf-8')
            magnet_link += f"&tr={tracker}"

        return magnet_link
    except Exception as e:
        print(f"Ошибка обработки {file_path}: {e}")
        return None


# Функция для обработки JSON-файла
def process_json(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Создаем временную папку для загрузки .torrent файлов
    temp_dir = "temp_torrents"
    os.makedirs(temp_dir, exist_ok=True)

    for entry in data["downloads"]:
        torrent_url = entry["uris"][0]  # Берем первую ссылку
        torrent_file = os.path.join(temp_dir, os.path.basename(torrent_url))

        # Скачиваем торрент файл
        downloaded_file = download_torrent(torrent_url, torrent_file)
        if downloaded_file:
            # Конвертируем в magnet-ссылку
            magnet_link = torrent_to_magnet(downloaded_file)
            if magnet_link:
                entry["uris"] = [magnet_link]  # Заменяем torrent ссылку на magnet
            else:
                print(f"Не удалось конвертировать {torrent_url}")
        else:
            print(f"Не удалось загрузить {torrent_url}")

    # Удаляем временные файлы
    for file in os.listdir(temp_dir):
        os.remove(os.path.join(temp_dir, file))
    os.rmdir(temp_dir)

    # Сохраняем обновленный JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Обновленный JSON сохранен в {output_file}")


# Основной скрипт
input_json = "downloads(t).json"  # Входной JSON файл
output_json = "downloads_updated.json"  # Выходной JSON файл
process_json(input_json, output_json)
