from notion.client import NotionClient
from tqdm import tqdm
import pandas as pd
import argparse
import time
import os
os.chdir(r'C:\Users\Takis\Google Drive\_projects_\medium-to-notion')


def parse_user_arg():
    parser = argparse.ArgumentParser(description="Parse links given a CSV file")
    parser.add_argument("-f","--file", help="filepath for csv that contains the links to parse")
    args = parser.parse_args()
    return args.file


def dataframe_to_collection(cv,df,properties_to_update):
    pstart = time.time()
    for index, row in tqdm(df.iterrows()):
        cv.refresh()
        collrow = cv.collection.add_row()
        for pp in properties_to_update:
            if row.get(pp):
                collrow.set_property(pp, row.get(pp))
        time.sleep(1)
    pend = time.time()
    print(f'>> Updating process lasted {pend - pstart}')
    print(f'>> Average update speed per item : {round((pend - pstart) / df.shape[0], 4)} seconds')


if __name__ == "__main__":

    # ------------------------------------------------------------------------------------------------------------
    # READ INPUT FILE
    # ------------------------------------------------------------------------------------------------------------
    # df = pd.read_pickle(r'.\parsed_links\parsed_links_df_971.pkl')
    filepath = parse_user_arg()
    print(f'Reading from {filepath}')
    df = pd.read_pickle(filepath)
    print(f'Size on input dataframe : {df.shape[0]}')


    # ------------------------------------------------------------------------------------------------------------
    # AUTHENTICATE
    # ------------------------------------------------------------------------------------------------------------
    # Obtain the `token_v2` value by inspecting your browser cookies on a logged-in session on Notion.so - browser cookies -> browser - notion - navigation bar - far left - lock sign
    print(f'Connecting to Notion...')
    client = NotionClient(token_v2="db9e74e9e002abe2090b6a68f07ee254c29351041f280402d9e2b4a56cfbbca33527dea5e0a6de459a8360187c9fca25a97158b73798371226b6ad9c4fc63db2329f747bbc048ac4249f465da25c")

    # ------------------------------------------------------------------------------------------------------------
    # INTERACT WITH NOTION PAGE
    # ------------------------------------------------------------------------------------------------------------

    # ACCESS 1
    # page = client.get_block("https://www.notion.so/takmers/fb1122c678d84e3cb5af1c7bbdfc75e7?v=02bd3babd6b9410f8e2f415e3dcf5aa7")
    # db = page.collection
    # cv = db._get_a_collection_view()

    # ACCESS 2
    cv = client.get_collection_view(
        'https://www.notion.so/takmers/fb1122c678d84e3cb5af1c7bbdfc75e7?v=c0388cb4e4274694b5aed87c4911bf02')
    print(f'Pulled in data successfully')

    # ------------------------------------------------------------------------------------------------------------
    # UPDATE DATABASE
    # ------------------------------------------------------------------------------------------------------------
    properties_to_update = [ 'url', 'title', 'text', 'summary', 'authors', 'publish_date', 'top_image' ]
    print(f'Started updating process..')
    dataframe_to_collection(cv, df, properties_to_update)

