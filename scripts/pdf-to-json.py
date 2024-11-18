import fitz  # PyMuPDF
import json

def extract_pdf_data(pdf_path):
    doc = fitz.open(pdf_path)
    
    # Список для хранения данных
    data = []
    
    # Проходим по каждой странице
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        text = page.get_text("text")  # Извлекаем текст с каждой страницы
        
        # Разбиваем текст на строки
        lines = text.split('\n')
        
        for line in lines:
            # Здесь можно добавить логику для извлечения данных
            if "viloyati" in line or "viloyati" in line:  # Ищем строки с названиями регионов
                region_name = line.strip()
                region_data = {"name": region_name, "districts": []}
                data.append(region_data)
            elif "tuman" in line:  # Ищем строки с названиями районов (tumanlar)
                district_name = line.strip()
                if data:
                    data[-1]["districts"].append(district_name)
    
    # Сохраняем в JSON файл
    with open('scripts/regions_and_districts.json', 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

# Запуск
pdf_path = 'scripts/uzb-alltumans.pdf'
extract_pdf_data(pdf_path)
