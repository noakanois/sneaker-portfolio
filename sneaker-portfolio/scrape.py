import requests
from fake_useragent import UserAgent
import json
import os
import time
import re

from bs4 import BeautifulSoup

ua = UserAgent()


def get_search_json(shoe_name):
    query_shoe_name = shoe_name.replace(" ", "+")
    headers = {
        "User-Agent": ua.random,
        "accept": "application/json",
        "accept-language": "en-US,en;q=0.9,de;q=0.8",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "no-cors",
        "sec-fetch-site": "cross-site",
    }
    url = f"https://stockx.com/en-gb/search/sneakers?s={query_shoe_name}"
    response = requests.get(url, headers=headers)
    
    soup = BeautifulSoup(response.content, 'html.parser')
    script_tag = soup.find('script', id='__NEXT_DATA__')

    json_string = re.search(r'{"props":.*}', script_tag.string, re.DOTALL).group()

    data = json.loads(json_string)
    data = data["props"]["pageProps"]["req"]["appContext"]["states"]["query"]["value"]["queries"]
    for da in data:
        try:
            new_data = da["state"]["data"]["browse"]["results"]["edges"]
            break
        except:
            continue

    sneakers = []
    for item in new_data:
        node = item["node"]
        if node["productCategory"] == "sneakers":
            sneaker_info = {
                "name": node["name"],
                "title": node["title"],
                "model": node["model"],
                "brand": node["brand"],
                "urlKey": node["urlKey"],
                "thumbUrl": node["media"]["thumbUrl"],
                "smallImageUrl": node["media"]["smallImageUrl"],
                "imageUrl": node["media"]["smallImageUrl"].split("?fit")[0],
                "description": node["description"],
                "retailPrice": 0,
                "releaseDate": ""
            }
            for trait in node["productTraits"]:
                sneaker_info[trait["name"]] = trait["value"]
            sneakers.append(sneaker_info)
            
    return sneakers

