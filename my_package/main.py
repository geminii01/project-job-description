import os
import datetime
import argparse
import pandas as pd
from wanted_crawling import wanted_crawling
from wanted_preprocessing import wanted_preprocessing
# from save_db import save_db


now = datetime.datetime.now()
ym_name = now.strftime('%Y%m')

def split_keywords(x):
    return [item.strip() for item in x.split(',')]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--keywords', type=split_keywords, required=True, help='Search keyword')
    # parser.add_argument('--host', required=True, help='Database host')
    # parser.add_argument('--user', required=True, help='Database user')
    # parser.add_argument('--password', required=True, help='Database password')
    # parser.add_argument('--port', type=int, required=True, help='Database port')
    args = parser.parse_args()
    
    search_keywords = args.keywords
    for search_keyword in search_keywords:
        config = wanted_crawling(search_keyword) # 크롤링
        wanted_preprocessing(config, search_keyword) # 전처리 및 데이터 저장

    path = './data/labeled'
    files = os.listdir(path)
    csv_files = [file for file in files if file.endswith('.csv')]

    dataframes = []
    for csv_file in csv_files:
        file_path = os.path.join(path, csv_file)
        df = pd.read_csv(file_path)
        dataframes.append(df)

    concat_df = pd.concat(dataframes, ignore_index=True)
    concat_df.to_csv(f'./data/final_data_{ym_name}.csv', index=False, encoding='utf-8-sig')

    # save_db(args.host, args.user, args.password, args.port)

if __name__ == "__main__":
    main()