from geocoding import Geocoder
from  scraping2 import Scarper
from udf import split_list
import pandas as pd
import os
import config as cg


def run(input_list):
    cities_splitted=split_list(input_list, 100)
    for i in range(len(cities_splitted)):
        scrapper = Scarper(scrapper_name=i, cities_l=cities_splitted[i])
        driver1 = scrapper.set_driver()
        data, skipped_items = scrapper.extract()
        pd.DataFrame(data).to_csv('final_' + scrapper1.get_name() + '.csv', index=False)
        print("skipped on: " + ','.join(skipped_items))
    files = [f for f in os.listdir() if f[-4:] == '.csv' and f[:5] == 'final']
    li = []
    for filename in files:
        df = pd.read_csv(filename, encoding='utf-8')
        if len(df) != 0:
            li.append(df)
    full_df = pd.concat(li,axis=0)
    df_list = full_df['city'].tolist()
    geo_coder = Geocoder(address=df_list)
    result = geo_coder.set_location()
    full_df['loc'] = result
    for filename in files:
        os.remove(filename)
    return full_df


if __name__ == 'main':
    cities = pd.read_csv('cities2.csv', encoding='windows-1255')
    cities_list = cities['שם_ישוב'].sample(10).str.strip().tolist()
    final = run (cities_list)
    pd.DataFrame(final).to_csv(cg.FINAL_FILE, index=False)