import requests
import json
from io import BytesIO
from PIL import Image
API_KEY = '40d1649f-0493-4b70-98ba-98533de7710b'
# Получаем toponym объекта по адресу


def geocode(address):
    params = {
        "apikey": API_KEY,
        "geocode": address,
        "format": "json"
    }

    try:
        js = requests.get("http://geocode-maps.yandex.ru/1.x/", params=params).json()
        features = js["response"]["GeoObjectCollection"]["featureMember"]
        return features[0]["GeoObject"] if features else None
    except:
        return None


def get_map(pos: tuple[float, float] or list[float, float], size: float, map_type: str, flag: list[float, float] or None=None):
    params = {
        "ll": "%f,%f" % (pos[0], pos[1]),
        "spn": "%f,%f" % (size, size),
        "l": map_type
    }

    if flag:
        params["pt"] = "%f,%f,comma" % (flag[0], flag[1])

    resp = requests.get("http://static-maps.yandex.ru/1.x/", params=params)

    if resp.status_code != 200:
        return

    image_type = "PNG"
    if map_type != "map":
        image_type = "JPG"

    return resp.content, image_type


def get_coordinates(address):
    toponym = geocode(address)
    if not toponym:
        return None
    # Координаты центра топонима:
    toponym_coodrinates = toponym["Point"]["pos"]
    # Широта, преобразованная в плавающее число:
    toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")
    return [float(toponym_longitude), float(toponym_lattitude)]


def get_ll_span(address):
    toponym = geocode(address)
    if not toponym:
        return (None, None)
    # Координаты центра топонима:
    toponym_coodrinates = toponym["Point"]["pos"]
    # Долгота и Широта :
    toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")
    # Собираем координаты в параметр ll (строка)
    ll = ",".join([toponym_longitude, toponym_lattitude])
    # Рамка вокруг объекта:
    envelope = toponym["boundedBy"]["Envelope"]
    # левая, нижняя, правая и верхняя границы из координат углов:
    l, b = envelope["lowerCorner"].split(" ")
    r, t = envelope["upperCorner"].split(" ")
    # Вычисляем полуразмеры по вертикали и горизонтали
    dx = abs(float(l) - float(r)) / 2.0
    dy = abs(float(t) - float(b)) / 2.0
    # Собираем размеры в параметр span
    span = f"{dx},{dy}"
    # Воpвращаем координаты ll и размеры объекта span
    return ll, span


def get_nearest_object(point, kind):
    ll = "{0},{1}".format(point[0], point[1])
    geocoder_request = f"http://geocode-maps.yandex.ru/1.x/"
    geocoder_params = {"apikey": API_KEY,
                       "geocode": ll,
                       "format": "json"}
    if kind:
        geocoder_params['kind'] = kind
    # Выполняем запрос к геокодеру, анализируем ответ.
    response = requests.get(geocoder_request, params=geocoder_params)
    if not response:
        raise RuntimeError(
            f"""Ошибка выполнения запроса:
    {geocoder_request}
    Http статус: {response.status_code,} ({response.reason})""")
    # Преобразуем ответ в json-объект
    json_response = response.json()
    # Получаем первый топоним из ответа геокодера.
    features = json_response["response"]["GeoObjectCollection"]["featureMember"]
    return features[0]["GeoObject"]["name"] if features else None


if __name__ == "__main__":
    img = get_map((37.53, 55.7), 0.002, "sat")
    Image.open(BytesIO(img)).show()
