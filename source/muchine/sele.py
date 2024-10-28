import os.path
import time
import random
import pandas as pd
from selenium import webdriver, common
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common import by
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.wait import WebDriverWait

df = pd.DataFrame({"카드명": [], "카드회사": [], "혜택1": [], "혜택2": [], "혜택3": []})
url = "https://www.card-gorilla.com/card?cate=CRD"
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get(url)

sel = "#q-app > section > div.card > section > div > div.card_list > div.ftr > a.lst_more"
for i in range(10):
    try:
        more_btn = WebDriverWait(driver, timeout=10).until(
            lambda d: d.find_element(by.By.CSS_SELECTOR, sel)
        )
        driver.execute_script("arguments[0].click();", more_btn)
        time.sleep(round(random.random() * 2, 2) + 2)
    except common.exceptions.TimeoutException as e:
        break


sel = "#q-app > section > div.card > section > div > div.card_list > ul > li"
cards = driver.find_elements(by.By.CSS_SELECTOR, sel)


for card in cards:
    tmp_list = []
    sel = "div"
    card_container = card.find_element(by.By.CSS_SELECTOR, sel)

    sel = "div.card_data > div.name > p > span"
    name = card_container.find_elements(by.By.CSS_SELECTOR, sel)

    for tag in name:
        tmp_list.append(tag.text)

    sel = "div.card_data > div.sale > p"
    sel_2 = "i"
    sel_3 = "span > b"
    sale = card_container.find_elements(by.By.CSS_SELECTOR, sel)

    for tag in sale:
        benefit_att = tag.find_element(by.By.CSS_SELECTOR, sel_2)
        benefit_num = tag.find_element(by.By.CSS_SELECTOR, sel_3)
        tmp_list.append(f"{benefit_att.text} {benefit_num.text}")
    while len(tmp_list) != 5:
        tmp_list.append(None)
    df.loc[len(df)] = tmp_list


save_path = "../data/card_info"
if not os.path.exists(save_path):
    os.makedirs(save_path)

df.to_csv(os.path.join(save_path, "cards.csv"), index=False)
driver.close()