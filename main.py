from geocoding import Geocoder
from  scraping2 import Scarper
from udf import split_list
import pandas as pd
import os
import config as cg
import logging
import sys


def run(input_list, retries=0, run_logger=None):
    skipped_list = []
    if run_logger:
        run_logger.info('splitting cities to lists')
    cities_splitted = split_list(input_list, 100)
    for i in range(len(cities_splitted)):
        scrapper = Scarper(scrapper_name=i, cities_l=cities_splitted[i], logger=run_logger)
        scrapper.set_driver()
        data, skipped_items = scrapper.extract()
        pd.DataFrame(data).to_csv('final_' + scrapper.get_name() + '.csv', index=False)
        print("skipped on: " + ','.join(skipped_items))
        skipped_list.append(skipped_items)
    if retries > 0:
        # code if you want to add more tries for skipped items
        pass
    if run_logger:
        run_logger.info('merging files')
    files = [f for f in os.listdir() if f[-4:] == '.csv' and f[:5] == 'final']
    li = []
    for filename in files:
        df = pd.read_csv(filename, encoding='utf-8')
        if len(df) != 0:
            li.append(df)
    full_df = pd.concat(li, axis=0)
    df_list = full_df['city'].tolist()
    if run_logger:
        run_logger.info('adding geocode')
    geo_coder = Geocoder(address=df_list, logger=run_logger)
    result = geo_coder.set_location()
    full_df['loc'] = result
    for filename in files:
        os.remove(filename)
    return full_df


if __name__ == 'main':
    logger = logging.getLogger('app')
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(created)f:%(levelname)s:%(name)s:%(module)s:%(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.info('starting logger')
    logger.info('reading cities list')
    cities = pd.read_csv('cities2.csv', encoding='windows-1255')
    cities_list = cities['שם_ישוב'].sample(10).str.strip().tolist()
    final = run(cities_list, run_logger=logger)
    pd.DataFrame(final).to_csv(cg.FINAL_FILE, index=False)
    logger.info('finished successfully')
    logger.removeHandler(handler)
    logging.shutdown()