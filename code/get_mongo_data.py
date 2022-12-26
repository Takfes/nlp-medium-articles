import pymongo
from pymongo import MongoClient
import pandas as pd
import config

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

# Get Collection Counts
col.count_documents({})

# Collect all data from the database
data = list(col.find({}))

# Retain only relevant columns
df = pd.DataFrame([{'title':x.get('title'),'text':x.get('text'),'url':x.get('url')} for x in data])

# Save dataframe to disk
df.to_pickle('articles.pkl')