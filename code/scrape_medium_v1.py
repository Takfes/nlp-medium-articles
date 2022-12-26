
import sys, os, time, json, requests, re, argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options


os.chdir(r'C:\Users\takis\Google Drive\_projects_\medium-to-notion')
saved_links_df = pd.read_pickle("data/title_link.pkl")

CHROME_DRIVER = r'C:\Users\takis\Google Drive\chromedriver.exe'
PAGE = "https://medium.com"
MEDIUM_BOOKMARKS_PAGE = "https://medium.com/me/list/queue"
EMAIL = 'pan.fessas@gmail.com'
PASSWORD = 'T28!1990akis'


def parse_user_arg():
    parser = argparse.ArgumentParser(description="Parse links given a CSV file")
    parser.add_argument("-f","--file", help="filepath for csv that contains the links to parse")
    args = parser.parse_args()
    return args.file


def browse_medium_bookmarks():

    global driver
    driver = webdriver.Chrome(CHROME_DRIVER)
    driver.get(PAGE)

    def navigate_to_xpath(xpath,keys=None):
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        temp_field = driver.find_element_by_xpath(xpath)
        if keys:
            temp_field.send_keys(keys)
        else :
            temp_field.click()

    # get started button
    navigate_to_xpath('//*[@id="top-nav-get-started-cta"]/div/span/a/button')
    # sign in button
    navigate_to_xpath('//*[@id="susi-modal-sign-up-link"]/div/h4/button/b')
    # google sign in button
    navigate_to_xpath('//*[@id="susi-modal-google-button"]/a/div')
    # type in email
    navigate_to_xpath('//*[@id="identifierId"]',EMAIL)
    # proceed
    navigate_to_xpath('//*[@id="identifierNext"]/div/button/div[2]')
    # type in password
    navigate_to_xpath('//*[@id="password"]/div[1]/div/div[1]/input', PASSWORD)
    # proceed
    navigate_to_xpath('//*[@id="passwordNext"]/div/button/div[2]')
    time.sleep(3)
    # go to bookmarks page
    driver.get(MEDIUM_BOOKMARKS_PAGE)
    # close pop up window
    navigate_to_xpath('/html/body/div[2]/div/div/div/div[1]/div/button')


def scroll_down():

    lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
    match = False
    while (match == False):
        lastCount = lenOfPage
        time.sleep(3)
        lenOfPage = driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;"
        )
        if lastCount == lenOfPage:
            match = True


def scroll_down_to_existing():

    lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
    match = False
    counter = 1

    while (match == False):

        print(f'Iteration {counter}')
        if counter % 5 == 0 :
            print(f'Cross Check with existing links {counter}')
            gather_links()
            diff_checker(saved_links_df, temp_df)
            if intersection :
                break

        lastCount = lenOfPage
        time.sleep(3)
        lenOfPage = driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;"
        )
        if lastCount == lenOfPage:
            match = True
        counter += 1


def gather_links():
    global temp_df
    # EXTRACT PAGE SOURCE AFTER SCROLLING
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'lxml')

    # BS4 to parse links so far
    # refresh the 'class_' component below
    divsoup = soup.find_all('div', class_ ="fk el fl fm")
    print(f'>> Count of items prior parsing {len(divsoup)}')

    titles, links = [], []
    for ds in divsoup:

        # scrape links
        link = (ds.find('a', href=True)['href'])
        link = link.replace('source=bookmarks', 'rr')
        if not link.startswith('https'):
            link = 'https://medium.com' + link
        links.append(link)

        # scrape title articles
        # refresh the 'class_' component below
        title = ds.find('h2', class_='ax gd cg az ge cj').text
        titles.append(title)

    print(f'>> Running Count of {len(titles)} titles with {len(links)} links')
    assert len(titles) == len(links)
    temp_df =  pd.DataFrame({'title' : titles, 'link' : links})


def diff_checker(saved_links_df,temp_df):
    global intersection
    global updated_title_link_df
    intersection = list(set(temp_df.title.tolist()).intersection(set(saved_links_df.title.tolist())))
    new_titles = list(set(temp_df.title.tolist()).difference(set(saved_links_df.title.tolist())))
    new_titles_df = temp_df.query(" title in @new_titles ")
    updated_title_link_df = pd.concat([new_titles_df, saved_links_df])


if __name__ == "__main__":

    start = time.time()
    browse_medium_bookmarks()
    scroll_down_to_existing()
    driver.close()
    print(f'Saving new file with {updated_title_link_df.shape[0]} rows')
    updated_title_link_df.to_pickle('data/title_link.pkl')
    end = time.time()
    print(f'Process took {end-start}')
