import os
import requests

API_KEY = os.environ["GOOGLE_API_KEY"]
SEARCH_ENGINE_ID = os.environ["GOOGLE_SEARCH_ENGINE_ID"]

url = "https://www.googleapis.com/customsearch/v1"

params = {
    "key": API_KEY,
    "cx": SEARCH_ENGINE_ID,
    "q": "constructoras Chile",
}

response = requests.get(url, params=params, timeout=10)

print("Código HTTP:", response.status_code)

data = response.json()

if response.status_code != 200:
    print("Error:")
    print(data)
else:
    print("¡Conexión exitosa!")
    
    for resultado in data.get("items", []):
        print()
        print("EMPRESA:", resultado.get("title"))
        print("WEB:", resultado.get("link"))
        print("DESCRIPCIÓN:", resultado.get("snippet"))