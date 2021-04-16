import requests
from bs4 import BeautifulSoup
r = requests.get("https://www.bbc.com/news/world-us-canada-56727154")
page = BeautifulSoup(r.text, 'html.parser')
print(page.text[: 10000])
