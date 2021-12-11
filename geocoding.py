import geopandas as gpd
from geopy.geocoders import Nominatim
import pycristoforo as pyc
import config as cg
import pandas as pd


class Geocoder:
    def __init__(self, address):
        self.address = address
        self.LOCATOR_NAME = cg.LOCATOR_NAME
        self.municipalities = gpd.read_file(cg.MUNICIPALITIES_FILENAME)
        self.longitude = []
        self.latitude = []

    def geocode(self, address):
        geo_locator = Nominatim(user_agent=self.LOCATOR_NAME)
        latitude = geo_locator.geocode(address).latitude
        longitude = geo_locator.geocode(address).longitude
        return [latitude, longitude]

    def city_exists(self, city):
        if self.municipalities[self.municipalities.MUN_HEB == city].shape[0] >= 1:
            return True
        else:
            return False

    def get_polygon(self, city):
        if self.city_exists(city):
            return self.municipalities[self.municipalities.MUN_HEB == city].geometry.values[0]
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
        return [self._set_location_single(city) for city in self.address]


if __name__ == '__main__':
    cities = pd.read_csv('final_one.csv', encoding='utf-8')
    cities_list = cities['city'].tolist()
    geocoder1 = Geocoder(address=cities_list)
    result = geocoder1.set_location()
    cities['loc'] = result
    pd.DataFrame(cities).to_csv('final_one_points.csv', index=False)





