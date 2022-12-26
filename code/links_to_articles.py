import sys, os, time, json, re, argparse
from datetime import datetime
import logging
import pandas as pd
from newspaper import Article
from tqdm import tqdm

# # make sure this is installed
# import nltk
# nltk.download('punkt')

def newspaper_wrapper(url):
    article_features = {}
    print(f"\Parsing url : {url}")
    try:
        print(50 * "=")
        start = time.time()
        article = Article(url)
        article.download()
        article.parse()
        article.nlp()
        article_features["url"] = url
        article_features["title"] = article.title
        article_features["text"] = article.text
        article_features["keywords"] = article.keywords
        article_features["summary"] = article.summary
        article_features["authors"] = article.authors
        article_features["tags"] = list(article.tags)
        article_features["publish_date"] = article.publish_date.strftime("%Y-%m-%d")
        article_features["parsed_date"] = datetime.now().strftime("%Y-%m-%d")
        article_features['html'] = article.html
        article_features['top_image'] = article.top_image
        article_features['images'] = list(article.images)
        article_features['links'] = article.extractor.get_urls(article.html)
        end = time.time()
        print(f"\nArticle {article_features['title']} parsed successfully")
        print(f"\nParsing took : {end-start:.2f}")
        return article_features

    except Exception as e:
        print(e)
        logging.error(f"{url}")


if __name__ == "__main__":

    timetag = datetime.now().strftime("%Y%m%d%H%M%S")

    logging.basicConfig(
        level=logging.ERROR,
        format="{asctime} {levelname:<8} {message}",
        style="{",
        filename=f"data/logs/newspaper_{timetag}.log",
        filemode="w",
    )

    df = pd.read_pickle("data/links_20221113.pkl")
    links = df.link.tolist()

    articles = []
    for link in tqdm(links):
        articles.append(newspaper_wrapper(link))

    with open(f"data/articles_{timetag}.json", "w") as f:
        json.dump(articles, f)
