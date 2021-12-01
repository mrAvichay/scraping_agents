#!/usr/bin/env python
# coding: utf-8
import pandas as pd
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, \
    ElementNotInteractableException, StaleElementReferenceException, \
    TimeoutException


class Scarper():
    def __init__(self, cities_l):
        self.cities = cities_l
        self.license, \
        self.name, \
        self.mail, \
        self.agency, \
        self.city, \
        self.is_pensioni, \
        self.is_elementar = ([] for i in range(7))
        self.ignored_exceptions = (NoSuchElementException, StaleElementReferenceException)
        self.site = "https://insa-prod-ex.formtitan.com/AgentsSearch#/"
        self.driver = webdriver.Chrome(ChromeDriverManager().install())

    def set_driver(self):
        # access site
        self.driver.get(self.site)
        self.driver.implicitly_wait(10)
        self.driver.maximize_window()
        return self.driver

    def extract(self):
        select_choice1 = WebDriverWait(self.driver, 10, ignored_exceptions=self.ignored_exceptions) \
            .until(EC.presence_of_element_located((By.CLASS_NAME, 'select2-choice')))
        select_choice1.click()
        agent_choice1 = WebDriverWait(self.driver, 10, ignored_exceptions=self.ignored_exceptions) \
            .until(EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='סוכן ביטוח']")))
        agent_choice1.click()
        for i in range(0, len(self.cities)):
            city_selected = self.cities[i]
            print(city_selected)
            try:
                search1 = WebDriverWait(self.driver, 10, ignored_exceptions=self.ignored_exceptions). \
                    until(EC.presence_of_element_located((By.ID, "e_1602060984227-254-72")))
                # search1 = driver.find_element(By.ID, "e_1602060984227-254-72")
                search1.send_keys(city_selected)
                search1.send_keys(Keys.RETURN)
            except TimeoutException:
                print('random error')
            try:
                search1 = WebDriverWait(self.driver, 10, ignored_exceptions=self.ignored_exceptions). \
                    until(EC.presence_of_element_located((By.ID, "e_1602060984227-254-72")))
                search1.send_keys(city_selected)
                search1.send_keys(Keys.RETURN)
            except TimeoutException:
                print('random error')
            try:
                self.driver.find_element(By.LINK_TEXT, "בחר").click()
                self.driver.find_element(By.ID, "e_1596528447512-995-1").click()  # perform search
            except NoSuchElementException as e:
                self.driver.find_element(By.CLASS_NAME, "close-button-div").click()  # close window in case of error
            try:
                correction_close = WebDriverWait(self.driver, 10) \
                    .until(EC.element_to_be_clickable((By.ID, "close_correction_error")))
                # print("alert accepted")
                correction_close.click()
            except TimeoutException:
                print("no alert")
                pass
            try:
                pages = int([int(e) for e in 
                             self.driver.find_element(By.XPATH, "//div[@class='TablePagerTotal']")
                            .get_attribute("innerText").split() 
                             if e.isdigit()][0] / 10) + 1
            except NoSuchElementException as e3:
                pages = 2
            try:
                for p in range(1, pages + 1):
                    table = self.driver.find_element(By.XPATH, "//table/tbody")
                    # append element to lists
                    # license
                    license.extend(
                        [el.get_attribute("innerText") for el in table.find_elements(By.XPATH, "//tr/td[1]")])
                    # name
                    name.extend([el.get_attribute("innerText") for el in table.find_elements(By.XPATH, "//tr/td[2]")])
                    # mail
                    mail.extend([el.get_attribute("innerText") for el in table.find_elements(By.XPATH, "//tr/td[3]")])
                    # agency
                    agency.extend([el.get_attribute("innerText") for el in table.find_elements(By.XPATH, "//tr/td[7]")])
                    # city
                    city.extend([city_selected] * len(table.find_elements(By.XPATH, "//tr/td[7]")))
                    # is pensioni
                    is_pensioni.extend(
                        [el.get_attribute("innerText") for el in table.find_elements(By.XPATH, "//tr/td[8]")])
                    # is elementar
                    is_elementar.extend(
                        [el.get_attribute("innerText") for el in table.find_elements(By.XPATH, "//tr/td[9]")])
                    self.driver.find_element(By.XPATH, "//a[@ng-switch-when='next']").click()  # click next
                    self.driver.implicitly_wait(10)
            except NoSuchElementException as e3:
                continue
        return {'license': self.license,
                'name': self.name,
                'city': self.city,
                'is_pensioni': self.is_pensioni,
                'is_elementar': self.is_elementar}


if __name__ == '__main__':
    cities = pd.read_csv('cities2.csv', encoding='windows-1255')
    cities_list = cities['שם_ישוב'].str.strip().tolist()
    scrapper1 = Scarper(cities_list)
    driver1 = Scarper.set_driver()
    data = Scarper.extract(cities_list)
    pd.DataFrame(data).to_csv('final.csv', index=False)
