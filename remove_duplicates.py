import json

def remove_duplicates(json_file, output_file):
    try:
        # Читаем исходный JSON
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if not isinstance(data, dict) or "downloads" not in data:
            print("Неверный формат JSON файла. Ожидается объект с ключом 'downloads'.")
            return

        unique_objects = []
        seen = set()

        for item in data["downloads"]:
            # Формируем уникальный идентификатор объекта
            identifier = (item.get("title"), tuple(item.get("uris", [])))

            if identifier not in seen:
                seen.add(identifier)
                unique_objects.append(item)

        # Обновляем данные и сохраняем
        data["downloads"] = unique_objects
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        print(f"Успешно удалено дублирующихся объектов. Итоговый файл сохранён как {output_file}.")

    except FileNotFoundError:
        print(f"Файл {json_file} не найден.")
    except json.JSONDecodeError:
        print(f"Ошибка чтения файла {json_file}: Неверный формат JSON.")
    except Exception as e:
        print(f"Произошла ошибка: {e}")

# Использование
remove_duplicates("downloads.json", "downloads_unique.json")
