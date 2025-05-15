import requests, json


def How_weather():
    res = requests.get(
        "https://api.openweathermap.org/data/2.5/weather?lat=60.613123&lon=56.837715&appid=eff217a91683da4bdc25b84b94101798").text
    res = json.loads(res)
    return res['weather'][0]['main']
