import requests
import re

# Функция для парсинга M3U плейлиста
def parse_m3u(url):
    """Парсит M3U файл и возвращает словарь групп."""
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Не удалось загрузить плейлист с URL: {url}")
    
    lines = response.text.splitlines()
    groups = {}
    current_group = None
    group_content = []

    # Извлекаем строку EXTINF и другие данные
    for line in lines:
        if line.startswith("#EXTINF"):
            # Извлекаем название группы из тега EXTGRP
            match = re.search(r'group-title="([^"]+)"', line)
            if match:
                group_name = match.group(1).strip()
                if group_name != current_group:
                    if current_group and group_content:
                        groups[current_group] = group_content
                    current_group = group_name
                    group_content = []
            group_content.append(line)
        elif line.startswith("#EXTVLCOPT") or line.startswith("http"):
            # Добавляем строки с EXTVLCOPT и ссылки
            group_content.append(line)

    # Добавляем последнюю группу
    if current_group and group_content:
        groups[current_group] = group_content

    return groups


# Функция для извлечения строк метаданных
def extract_metadata(url):
    """Извлекает строки метаданных из целевого плейлиста."""
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Не удалось загрузить плейлист с URL: {url}")
    
    lines = response.text.splitlines()
    metadata_lines = []

    for line in lines:
        if line.startswith("#EXTM3U") or line.startswith("#---"):
            metadata_lines.append(line)  # Сохраняем строки с метаданными

    return metadata_lines


# Функция для обновления плейлиста
def update_playlist(source_urls, target_url, output_file, special_group=None, special_source=None):
    """Обновляет целевой плейлист на основе одного или нескольких исходников."""
    target_groups = parse_m3u(target_url)
    
    # Обновляем группы из первого исходника
    source_groups = parse_m3u(source_urls[0])
    for group, channels in source_groups.items():
        if group in target_groups:
            print(f"Обновляется группа: {group} из первого исходника")
            target_groups[group] = channels  # Заменяем содержимое группы
    
    # Обновляем специальную группу из второго исходника
    if special_group and special_source:
        special_source_groups = parse_m3u(special_source)
        if special_group in special_source_groups:
            print(f"Обновляется группа: {special_group} из второго исходника")
            target_groups[special_group] = special_source_groups[special_group]
        else:
            print(f"Группа '{special_group}' не найдена во втором исходнике")

    # Извлекаем строки метаданных
    metadata_lines = extract_metadata(target_url)

    # Формируем обновлённый плейлист
    with open(output_file, "w", encoding="utf-8") as f:
        # Добавляем строки метаданных
        for metadata_line in metadata_lines:
            f.write(f"{metadata_line}\n")
        
        # Добавляем группы и каналы
        for group, channels in target_groups.items():
            for channel in channels:
                f.write(f"{channel}\n")
    
    print(f"Плейлист успешно обновлён и сохранён в {output_file}!")


# Основная функция
if __name__ == "__main__":
    # URL исходных плейлистов
    source_url_1 = "https://raw.githubusercontent.com/IPTVSHARED/iptv/refs/heads/main/IPTV_SHARED.m3u"
    source_url_2 = "https://raw.githubusercontent.com/Dimonovich/TV/Dimonovich/FREE/TV"
    target_url = "https://raw.githubusercontent.com/dikai669/playlist/refs/heads/main/mpll.m3u"
    output_file = "mpll.m3u"

    # Название группы для обновления из второго исходника
    special_group = "Lime (VPN 🇷🇺)"

    # Обновляем плейлист
    try:
        update_playlist(
            source_urls=[source_url_1, source_url_2],
            target_url=target_url,
            output_file=output_file,
            special_group=special_group,
            special_source=source_url_2
        )
    except Exception as e:
        print(f"Ошибка: {e}")
