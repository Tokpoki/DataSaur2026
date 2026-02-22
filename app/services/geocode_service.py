import requests
import time
import re
from sqlalchemy.orm import Session
from ..models import BusinessUnit


# 🔥 Очистка адреса
def clean_address(address: str):

    if not address:
        return ""

    address = address.lower()

    replacements = {
        "пр.": "проспект",
        "пр-т": "проспект",
        "ул.": "улица",
        "д.": "",
    }

    for k, v in replacements.items():
        address = address.replace(k, v)

    # Убираем всё после первой запятой
    address = address.split(",")[0]

    # Убираем БЦ и всё после него
    address = re.sub(r'бц.*', '', address)

    # Убираем этажи
    address = re.sub(r'\b\d+\s*этаж\b', '', address)

    # Убираем НП, ст, офис
    address = re.sub(r'\b(нп|ст|офис)\b.*', '', address)

    # Убираем текст в кавычках
    address = re.sub(r'".*?"', '', address)

    # Убираем лишние точки
    address = address.replace(".", " ")

    return address.strip()


# 🔥 Геокодинг с fallback логикой
def geocode_address(address: str, city: str):

    cleaned = clean_address(address)

    queries = [
        f"{cleaned}, {city}, Kazakhstan",
        f"{cleaned}, {city}",
        f"{city}, Kazakhstan"
    ]

    url = "https://nominatim.openstreetmap.org/search"

    headers = {
        "User-Agent": "fire-hackathon-app"
    }

    for query in queries:

        print(f"Пробуем запрос: {query}")

        params = {
            "q": query,
            "format": "json",
            "limit": 1
        }

        response = requests.get(url, params=params, headers=headers)

        if response.status_code == 200:
            data = response.json()
            if data:
                print(f"✔ Найдено по запросу: {query}")
                return float(data[0]["lat"]), float(data[0]["lon"])

        time.sleep(1)  # соблюдаем лимит Nominatim

    print(f"❌ Не удалось найти координаты даже по городу: {city}")
    return None, None


# 🔥 Заполнение координат офисов
def fill_office_coordinates(db: Session):

    offices = db.query(BusinessUnit).filter(
        BusinessUnit.latitude == None
    ).all()

    for office in offices:

        print("===================================")
        print(f"Геокодируем: {office.office_name}")
        print(f"Исходный адрес: {office.address}")

        lat, lon = geocode_address(
            office.address,
            office.office_name  # город
        )

        if lat and lon:
            office.latitude = lat
            office.longitude = lon
            db.commit()
            print(f"✅ Сохранено: {lat}, {lon}")
        else:
            print("❌ Координаты не найдены")

        time.sleep(1)

    print("🎯 Геокодирование завершено")