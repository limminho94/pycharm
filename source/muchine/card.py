from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.parse import quote


url_wikipedia = "https://www.card-gorilla.com/card?cate=CRD"


html = urlopen(url_wikipedia)


bs = BeautifulSoup(html.read(), features="html.parser")


card_info = bs.find_all("div", "card-container")
print(card_info)