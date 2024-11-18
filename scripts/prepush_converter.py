import json

# Загружаем JSON с регионами и округами
with open('scripts/regions_and_districts.json', 'r', encoding='utf-8') as file:
    regions_data = json.load(file)

# Установим отображение регионов на их ID, например:
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

# Преобразуем структуру данных
formatted_data = []

for region in regions_data:
    region_name = region['name']
    region_id = region_mapping.get(region_name, None)  # Присваиваем ID для региона
    if region_id:
        district_data = {
            'name': region_name,
            'districts': [{'name': district, 'region': region_id} for district in region['districts'] if 'tuman' in district.lower()]
        }
        formatted_data.append(district_data)

# Сохраняем в новый файл
with open('formatted_regions_and_districts.json', 'w', encoding='utf-8') as f:
    json.dump(formatted_data, f, ensure_ascii=False, indent=4)