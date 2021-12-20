import geopandas as gpd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import pycristoforo as pyc
import config as cg
import pandas as pd
import pickle
import logging
import sys


class Geocoder:
    def __init__(self, address, logger=None):
        self.address = address
        self.logger = logger
        self.LOCATOR_NAME = cg.LOCATOR_NAME
        self.municipalities = gpd.read_file(cg.MUNICIPALITIES_FILENAME)
        self.longitude = []
        self.latitude = []
        if self.logger:
            logger.info('loading cities matches')
        with open(cg.CITIES_DICT, 'rb') as handle:
            self.dict_cities = pickle.load(handle)

    def geocode(self, address):
        geo_locator = Nominatim(user_agent=self.LOCATOR_NAME, timeout=None)
        geocode = RateLimiter(geo_locator.geocode, min_delay_seconds=1)
        try:
            latitude = geocode(address).latitude
            longitude = geocode(address).longitude
        except AttributeError as e:
            latitude = 0
            longitude = 0
        return [latitude, longitude]

    def city_exists(self, city):
        if self.municipalities[self.municipalities.MUN_HEB == city].shape[0] >= 1:
            return True
        else:
            return False

    def city_match(self, city):
        if self.dict_cities.get(city) == '':
            return None
        else:
            return self.dict_cities.get(city)

    def get_polygon(self, city):
        if self.city_exists(city) and self.city_match(city):
            return self.municipalities[self.municipalities.MUN_HEB == self.city_match(city)].geometry.values[0]
        else:
            return None

    def _set_location_single(self, city):
        polygon_city = self.get_polygon(city)
        if polygon_city:
            return pyc.geoloc_generation(polygon_city,
                                         num=1,
                                         key=city)[0]['geometry']['coordinates']
        else:
            return self.geocode(city)

    def set_location(self):
        if self.logger:
            self.logger.info('running geocodes...')
        return [self._set_location_single(city) for city in self.address]


if __name__ == '__main__':
    logger = logging.getLogger('app')
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(created)f:%(levelname)s:%(name)s:%(module)s:%(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.info('starting logger')
    logger.info('reading file')
    cities = pd.read_csv('final_8.csv', encoding='utf-8')
    cities_list = cities['city'].tolist()
    geocoder1 = Geocoder(address=cities_list, logger=logger)
    result = geocoder1.set_location()
    cities['loc_X'] = [loc[0] for loc in result]
    cities['loc_Y'] = [loc[1] for loc in result]
    pd.DataFrame(cities).to_csv('final_8_points.csv', index=False)





