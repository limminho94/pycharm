from bs4 import BeautifulSoup
from urllib.request import urlopen
from  urllib.parse import quote


url_wikipedia = "https://ko.wikipedia.org/wiki/"
target = "뷰티풀_수프_(HTML_파서)"


html = urlopen(url_wikipedia + quote(target, safe=""))


bs = BeautifulSoup(html.read(), features="html.parser")
# print(bs.prettify)


link_list = bs.find_all(name="a")
# for link in link_list:
    # print(link)


table_data = bs.find("table", "infobox vevent")
# print(table_data)


table_body = table_data.find("tbody")
# print(table_body)


th_list = []
td_list = []
for i, tr in enumerate(table_body.find_all("tr")):
    if tr.find("th") is not None:
        th_list.append(tr.find("th").text)
        td_list.append(tr.find("td").text)
    else:
        print(i)