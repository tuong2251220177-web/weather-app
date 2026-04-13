from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import requests

app = FastAPI(title="Weather Vietnam App")
templates = Jinja2Templates(directory="templates")

CITIES = {
    "Hà Nội": {"lat": 21.0285, "lon": 105.8542},
    "Đà Nẵng": {"lat": 16.0544, "lon": 108.2022},
    "Hồ Chí Minh": {"lat": 10.8231, "lon": 106.6297},
}


CURRENCY_DISPLAY = {
    "USD": {"name": "Đô la Mỹ",        "flag": "🇺🇸"},
    "EUR": {"name": "Euro",             "flag": "🇪🇺"},
    "GBP": {"name": "Bảng Anh",         "flag": "🇬🇧"},
    "JPY": {"name": "Yên Nhật",         "flag": "🇯🇵"},
    "CNY": {"name": "Nhân dân tệ",      "flag": "🇨🇳"},
    "KRW": {"name": "Won Hàn Quốc",     "flag": "🇰🇷"},
    "SGD": {"name": "Đô la Singapore",  "flag": "🇸🇬"},
    "AUD": {"name": "Đô la Úc",         "flag": "🇦🇺"},
    "THB": {"name": "Baht Thái",        "flag": "🇹🇭"},
}

WEATHER_INFO = {
    0: {"text": "Trời quang", "icon": "☀️"},
    1: {"text": "Khá quang đãng", "icon": "🌤️"},
    2: {"text": "Có mây", "icon": "⛅"},
    3: {"text": "Nhiều mây", "icon": "☁️"},
    45: {"text": "Sương mù", "icon": "🌫️"},
    48: {"text": "Sương mù đóng băng", "icon": "🌫️"},
    51: {"text": "Mưa phùn nhẹ", "icon": "🌦️"},
    53: {"text": "Mưa phùn vừa", "icon": "🌦️"},
    55: {"text": "Mưa phùn dày", "icon": "🌧️"},
    56: {"text": "Mưa phùn lạnh nhẹ", "icon": "🌧️"},
    57: {"text": "Mưa phùn lạnh dày", "icon": "🌧️"},
    61: {"text": "Mưa nhẹ", "icon": "🌦️"},
    63: {"text": "Mưa vừa", "icon": "🌧️"},
    65: {"text": "Mưa to", "icon": "🌧️"},
    66: {"text": "Mưa lạnh nhẹ", "icon": "🌧️"},
    67: {"text": "Mưa lạnh to", "icon": "🌧️"},
    71: {"text": "Tuyết nhẹ", "icon": "🌨️"},
    73: {"text": "Tuyết vừa", "icon": "🌨️"},
    75: {"text": "Tuyết dày", "icon": "❄️"},
    77: {"text": "Hạt tuyết", "icon": "❄️"},
    80: {"text": "Mưa rào nhẹ", "icon": "🌦️"},
    81: {"text": "Mưa rào vừa", "icon": "🌧️"},
    82: {"text": "Mưa rào mạnh", "icon": "⛈️"},
    85: {"text": "Mưa tuyết nhẹ", "icon": "🌨️"},
    86: {"text": "Mưa tuyết mạnh", "icon": "🌨️"},
    95: {"text": "Dông", "icon": "⛈️"},
    96: {"text": "Dông kèm mưa đá nhẹ", "icon": "⛈️"},
    99: {"text": "Dông kèm mưa đá mạnh", "icon": "⛈️"},
}


def get_weather(lat: float, lon: float):
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&current=temperature_2m,wind_speed_10m,relative_humidity_2m,weather_code"
        "&timezone=auto"
    )

    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()
    current = data.get("current", {})

    weather_code = current.get("weather_code", -1)
    weather_meta = WEATHER_INFO.get(
        weather_code,
        {"text": f"Mã thời tiết: {weather_code}", "icon": "🌍"}
    )

    return {
        "temperature": current.get("temperature_2m", "N/A"),
        "windspeed": current.get("wind_speed_10m", "N/A"),
        "humidity": current.get("relative_humidity_2m", "N/A"),
        "description": weather_meta["text"],
        "icon": weather_meta["icon"],
        "time": current.get("time", "N/A"),
    }


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request, "index.html", {})


@app.get("/thoi-tiet", response_class=HTMLResponse)
def weather_page(request: Request):
    weather_data = []

    for city, coords in CITIES.items():
        try:
            weather = get_weather(coords["lat"], coords["lon"])
            weather_data.append({
                "city": city,
                **weather,
                "error": None,
            })
        except Exception as e:
            weather_data.append({
                "city": city,
                "error": f"Không lấy được dữ liệu: {str(e)}",
            })

    return templates.TemplateResponse(
        request,
        "weather.html",
        {
            "weather_data": weather_data
        }
    )


def get_exchange_rates():
    url = "https://open.er-api.com/v6/latest/USD"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()
    rates = data.get("rates", {})
    vnd_per_usd = rates.get("VND", 0)

    result = []
    for code, info in CURRENCY_DISPLAY.items():
        if code == "USD":
            vnd_rate = vnd_per_usd
        elif code in rates and rates[code] != 0:
            vnd_rate = vnd_per_usd / rates[code]
        else:
            vnd_rate = None

        result.append({
            "code": code,
            "name": info["name"],
            "flag": info["flag"],
            "vnd_rate": round(vnd_rate) if vnd_rate else "N/A",
        })

    return result, data.get("time_last_update_utc", "N/A")


@app.get("/ty-gia", response_class=HTMLResponse)
def exchange_rates(request: Request):
    try:
        rates, updated = get_exchange_rates()
        error = None
    except Exception as e:
        rates = []
        updated = "N/A"
        error = f"Không lấy được dữ liệu: {str(e)}"

    return templates.TemplateResponse(
        request,
        "exchange.html",
        {
            "rates": rates,
            "updated": updated,
            "error": error,
        }
    )