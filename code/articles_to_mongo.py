import json
import pandas as pd
from datetime import datetime
import pymongo
from pymongo import MongoClient
from pprint import pprint
import config

# Read articles from disk
with open("data/articles_20221113184305.json") as f:
    raw_data = json.load(f)

# Data cleansing - Remove duplicate articles
deduplicated_data = {}
for x in raw_data:
    if x:
        if x["title"]:
            deduplicated_data[x.get("title")] = x

print(f"raw data size : {len(raw_data)}")
print(f"deduplicacted data size : {len(deduplicated_data)}")
print(f"cleaned data size : {len(raw_data) - len(deduplicated_data)}")

data = list(deduplicated_data.values())

# # Save title-link tuple to disk
# links = {x.get('title'):x.get('url') for x in data}
# linksdf = pd.DataFrame().from_dict(links,orient='index').rename_axis('title').rename(columns={0:'url'}).reset_index()
# linksdf.to_pickle('data/title_link_20221113184305.pkl')

# Data preparation - remove html key
keys_before = list(data[0].keys())
keys_before
for x in data:
    del x["html"]
    del x["images"]
    del x["links"]
keys_after = list(data[0].keys())
keys_removed = list(set(keys_before).difference(set(keys_after)))
print(f"removed keys : {keys_removed}")

# Connect to Mongo Client
client = pymongo.MongoClient(
    f"mongodb+srv://{config.MONGOUSER}:{config.MONGOPASS}@cluster0.v6cpwum.mongodb.net/?retryWrites=true&w=majority"
)
try:
    print(client.server_info())
except Exception:
    print("Unable to connect to the server.")

# Create database if not exists
databases = client.list_database_names()
database_name = "application"

if not database_name in databases:
    db = client[database_name]
    print(f'database "{database_name}" created')
else:
    print(f'database "{database_name}" already exists')
    db = client.get_database(database_name)

# Create collection if not exists
collections = db.list_collection_names()
collection_name = "articles"

if not collection_name in collections:
    col = db[collection_name]
else:
    print(f'collection "{collection_name}" already exists')
    col = db[collection_name]

# # Upload many documents to the collection
# data[0].update({'source' : 'medium'})
col.insert_many(data)

# # How to drop database
# client.drop_database('articles')
# # How to drop collection
# col.drop()

# # Basic interactions
# # Count items in the database
# col.count_documents({})

# # Upload one document to the collection
# data[0].update({'source' : 'medium'})
# col.insert_one(data[0])

# # Delete all documents from a collection
# col.delete_many({})

# # Basic querying
# results = list(col.find())
# len(results)
# [x.get("title") for x in results]
# results[0]

# # Index
# pprint(db.articles.index_information())
# pprint(col.index_information())
# db.articles.get_indexes

# # Filter
# list(col.find({"title": "Easily edit DataFrames within JupyterLab"}))