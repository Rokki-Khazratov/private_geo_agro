import requests
import json

# Загружаем файл с районами
with open('scripts/formatted_regions_and_districts.json', 'r', encoding='utf-8') as json_file:
    regions_and_districts = json.load(json_file)

# Маппинг для привязки регионов к их ID
region_mapping = {
    "Tashkent": 1,
    "Jizzax viloyati": 2,
    "Namangan viloyati": 3,
    "Andijon viloyati": 4,
    "Buxoro viloyati": 5,
    "Fargʻona viloyati": 6,
    "Xorazm viloyati": 7,
    "Navoiy viloyati": 8,
    "Qashqadaryo viloyati": 9,
    "Qoraqalpogʻiston Respublikasi": 10,
    "Samarqand viloyati": 11,
    "Sirdaryo viloyati": 12,
    "Surxondaryo viloyati": 13,
    "Toshkent viloyati": 14
}

# URL для POST запроса
url = 'http://127.0.0.1:8000/api/districts/create/'

# Проходим по каждому региону и отправляем POST запрос для каждого района
for region in regions_and_districts:
    region_name = region['name']
    region_id = region_mapping.get(region_name)

    if region_id:
        for district in region['districts']:
            # Если данные о районе представляют собой строку, проверим это и отправим запрос
            if isinstance(district, str):
                district_name = district
            elif isinstance(district, dict) and 'name' in district:
                # Если данные о районе — это словарь, то извлекаем название
                district_name = district['name']
            else:
                district_name = None

            # Если название округа найдено и оно содержит 'tuman', отправляем POST запрос
            if district_name and 'tuman' in district_name.lower():
                payload = {
                    "region": region_id,  # Передаем ID региона
                    "name": district_name
                }

                # Отправляем POST запрос
                response = requests.post(url, json=payload)

                # Проверяем ответ
                if response.status_code == 201:
                    print(f"District '{district_name}' added successfully.")
                else:
                    print(f"Failed to add district '{district_name}': {response.text}")
            else:
                print(f"District '{district_name}' is not a valid 'tuman'. Skipping.")
    else:
        print(f"Region '{region_name}' not found in region mapping.")