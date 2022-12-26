import sys, os, time, json, requests, re, argparse
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
import config

CHROME_DRIVER = Path("/usr/local/bin/chromedriver")
IMPLICIT_WAIT = 30
PAGE = "https://medium.com"
READING_LIST_PAGE = 'https://medium.com/@pan.fessas/list/reading-list'
SCROLL_PAUSE_TIME = 4
MINS_TO_RUN = 10

def strip_title(tag):
    return " ".join(list(tag.children)[0].text.strip().replace('\n','').split())

def strip_href(tag):
    temp = tag.get('href')
    return temp if temp.startswith('https') else 'https://medium.com' + temp

def strip_author(tag):
    return ' '.join(list(list(tag.parents)[9].children)[1].p.text.strip().replace('\n','').split())

def strip_topic(tag):
    return ' '.join(list(list(tag.parents)[1].children)[-2].a.text.strip().replace('\n','').split())

def get_driver():
    options = uc.ChromeOptions()
    # go headless
    options.headless=True
    options.add_argument('--headless')
    # dont load images
    prefs_no_img={"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option('prefs', prefs_no_img)
    # enable cache
    prefs_cache={'disk-cache-size': 4096}
    options.add_experimental_option('prefs', prefs_cache)
    # extras
    options.add_argument('--ignore-certificate-errors')
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    options.add_argument('--incognito')
    # make driver
    driver = uc.Chrome(chrome_options=options,use_subprocess=True)
    driver.implicitly_wait(IMPLICIT_WAIT)
    return (driver)

# driver = get_driver()
driver = uc.Chrome(use_subprocess=True)
driver.implicitly_wait(IMPLICIT_WAIT)
driver.get(PAGE)

xpath_map = {
    'cookies':"(//button[position()=last()])[last()]",
    'sign_in':'//a[text()="Sign In"]',
    'sign_in_google':'//div[text()="Sign in with Google"]',
    'enter_email':"//input[@type='email']",
    'enter_pass':"//input[@type='password']",
    'anchor':"//p[contains(text(),'stories')]"
}

driver.find_element(By.XPATH,xpath_map.get('cookies')).click()
driver.find_element(By.XPATH,xpath_map.get('sign_in')).click()
driver.find_element(By.XPATH,xpath_map.get('sign_in_google')).click()

so_email = driver.find_element(By.XPATH,xpath_map.get('enter_email'))
so_email.send_keys(config.EMAIL)
so_email.send_keys(Keys.RETURN)

so_pass = so_email = driver.find_element(By.XPATH,xpath_map.get('enter_pass'))
so_email.send_keys(config.EMAIL)
so_email.send_keys(Keys.RETURN)

driver.get(READING_LIST_PAGE)

# TODO : DOM needs to be parsed incrementally otherwise gets massive
# from : https://stackoverflow.com/questions/20986631/how-can-i-scroll-a-web-page-using-selenium-webdriver-in-python
start = time.time()
while (time.time() - start)<(MINS_TO_RUN*60):
    # Scroll down to bottom
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    # Wait to load page
    time.sleep(SCROLL_PAUSE_TIME)


# TODO : save parsed DOM to html    
# html = driver.execute_script("return document.body.innerHTML;")
# with open("dom.html","w") as f:
#     f.write(html)
# with open("medium_soup.html") as f:
#     soup = BeautifulSoup(f,'html.parser')


page_source = driver.page_source
soup = BeautifulSoup(page_source, "lxml")
soupa = soup.find_all('a',{"aria-label" : "Post Preview Title"})
print(f'soup length : {len(soupa)}')

parsed_soup = []
for tag in soupa:
    fields = {
        'title'  : strip_title(tag),
        'link'   : strip_href(tag),
        'author' : strip_author(tag),
        'topic'  : strip_topic(tag)
        }
    parsed_soup.append(fields)

df = pd.DataFrame(parsed_soup)
df.to_pickle('/data/medium_links.pkl')