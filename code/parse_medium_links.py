import newspaper
from newspaper import Article
import json, os, time
from datetime import datetime
import pickle
import nltk
# nltk.download('punkt')
import pandas as pd
from tqdm import tqdm
import argparse
import os
os.chdir(r'C:\Users\Takis\Google Drive\_projects_\medium-to-notion')

def parse_user_arg():
    parser = argparse.ArgumentParser(description="Parse links given a CSV file")
    parser.add_argument("-f","--file", help="filepath for csv that contains the links to parse")
    args = parser.parse_args()
    return args.file

def newspaper_wrapper(url):
    article_features = {}
    print(f'\nPrepare to parse url : {url}')
    try:
        start = time.time()
        article = Article(url)
        article.download()
        article.parse()
        article.nlp()
        article_features['url'] = url
        article_features['title'] = article.title
        article_features['text'] = article.text
        article_features['keywords'] = article.keywords
        article_features['summary'] = article.summary
        article_features['language'] = article.meta_lang
        article_features['authors'] = article.authors[0]
        article_features['publish_date'] = article.publish_date.strftime("%Y-%m-%d")
        article_features['tags'] = list(article.tags)
        article_features['top_image'] = article.top_image
        article_features['images'] = list(article.images)
        article_features['parsed_date'] = datetime.now().strftime("%Y-%m-%d")
        article_features['parse_duration'] = str(time.time()-start)
        # article_features['links'] = article.extractor.get_urls(article.html)
        print(f"\nParsing for article titled : {article_features['title']}")
        print(f"\nParsing lasted : {article_features['parse_duration']}")

    except Exception as e:
        print(e)
        print(f'\nParsing for {url} failed')
        article_features = url
    finally:
        print(50*'=')
        return article_features

if __name__ == "__main__":

    # ------------------------------------------------------------------------------------------------------------
    # READ INPUT FILE
    # ------------------------------------------------------------------------------------------------------------
    # filepath = r'.\data\title_link.pkl'
    filepath = parse_user_arg()
    print(f'Reading from {filepath}')
    df = pd.read_pickle(filepath)

    # ------------------------------------------------------------------------------------------------------------
    # PARSE LINKS
    # ------------------------------------------------------------------------------------------------------------
    pstart = time.time()
    parsed_items = [newspaper_wrapper(link) for link in tqdm(df.link.tolist())]
    pend = time.time()
    print(f'>> Parsing process lasted {pend-pstart}')
    print(f'>> Average parse speed : {round((pend-pstart)/len(parsed_items),4)} seconds')

    # ------------------------------------------------------------------------------------------------------------
    # CLEANUP OUTPUT
    # ------------------------------------------------------------------------------------------------------------
    successful_items = [x for x in parsed_items if isinstance(x,dict)]
    failed_items = [x for x in parsed_items if isinstance(x,str)]
    print(f'>> Successfully parsed {len(successful_items)}/{len(parsed_items)} -{round(len(successful_items)/len(parsed_items),4)*100}%- links')
    print(f'>> Failed to parse {len(failed_items)} links')

    # ------------------------------------------------------------------------------------------------------------
    # ATTEMPT TO REMEDY FAILED ITEMS AND RETRY
    # ------------------------------------------------------------------------------------------------------------
    remedy_fails = [ 'https://' + x for x in failed_items if x.startswith('medium') ]
    retry_parsed_items = [ newspaper_wrapper(link) for link in tqdm(remedy_fails) ]
    retry_successful_items = [ x for x in retry_parsed_items if isinstance(x, dict) ]
    retry_failed_items = [ x for x in retry_parsed_items if isinstance(x, str) ]

    # ------------------------------------------------------------------------------------------------------------
    # GATHER OUTPUT IN DATAFRAMES
    # ------------------------------------------------------------------------------------------------------------
    data = pd.DataFrame(successful_items)
    # data = pd.DataFrame(successful_items + retry_successful_items)
    # failed_data = pd.DataFrame({'link' : pd.Series(retry_failed_items)})

    # ------------------------------------------------------------------------------------------------------------
    # SAVE SUCCESSFUL OUTPUT IN A PICKLE
    # ------------------------------------------------------------------------------------------------------------
    filename = r'.\data\title_link_parsed.pkl'
    data.to_pickle(filename)
    print(f'Parsed articles saved into {filename}')

    # ------------------------------------------------------------------------------------------------------------
    # TRACK FAILS IN A CSV
    # ------------------------------------------------------------------------------------------------------------
    fname = filepath.replace("medium_links_df","failed_medium_links_df")
    data.to_csv(filename, index=False)
    print(f'Failed articles saved into {fname}')

    df.to_clipboard()
    ll = df.link.tolist()
    aa = newspaper_wrapper('https://uanurag6212.medium.com/loss-function-its-types-in-neural-network-79f4abdd6883?rr---------0----------------------------')
    bb = newspaper_wrapper('https://medium.com/medium.com/neptune-ai/hyperparameter-tuning-in-python-a-complete-guide-2020-cfd8886c784b?rr---------1----------------------------')

    len(ll)
    gg = []
    for l in ll[:10]:
        temp = newspaper_wrapper(l)
        # l = l.replace('https://medium.com','https://medium.com/')
        # if not l.startswith('https'):
        #     l = 'https://medium.com' + l
        gg.append(l)

    len(gg)
    df.link = gg
    df.to_pickle(r'.\data\title_link.pkl')
