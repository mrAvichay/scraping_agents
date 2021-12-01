import pandas as pd
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
import config as cg


class Scarper:
    def __init__(self,name, cities_l):
        self.name = name
        self.cities = cities_l
        self.license, \
        self.name, \
        self.mail, \
        self.agency, \
        self.city, \
        self.is_pensioni, \
        self.is_elementar = ([] for i in range(7))
        self.ignored_exceptions = (NoSuchElementException, StaleElementReferenceException)
        self.site = cg.SITE
        self.driver = webdriver.Chrome(ChromeDriverManager().install())
        self.skipped = []

    def set_driver(self):
        # access site
        self.driver.get(self.site)
        self.driver.implicitly_wait(10)
        self.driver.maximize_window()
        return self.driver

    def get_name(self):
        return self.name

    def extract(self):
        select_choice1 = WebDriverWait(self.driver, 10, ignored_exceptions=self.ignored_exceptions) \
            .until(EC.presence_of_element_located((By.CLASS_NAME, cg.DROP_DOWN_LICENSE)))
        select_choice1.click()
        agent_choice1 = WebDriverWait(self.driver, 10, ignored_exceptions=self.ignored_exceptions) \
            .until(EC.element_to_be_clickable((By.XPATH, cg.AGENT_DD_CHOICE)))
        agent_choice1.click()
        for i in range(0, len(self.cities)):
            city_selected = self.cities[i]
            print(city_selected)
            try:
                search1 = WebDriverWait(self.driver, 10, ignored_exceptions=self.ignored_exceptions). \
                    until(EC.presence_of_element_located((By.ID, cg.SEARCH_BOX)))
                search1.send_keys(city_selected)
                search1.send_keys(Keys.RETURN)
            except TimeoutException:
                print('random error')
                self.skipped.append(city_selected)
                continue
            try:
                self.driver.find_element(By.LINK_TEXT, cg.LINK_SELECT).click()
                self.driver.find_element(By.ID, cg.SEARCH_BUTTON).click()  # perform search
            except NoSuchElementException as e:
                self.driver.find_element(By.CLASS_NAME, cg.SELECT_CLOSE_BUTTON).click()  # close window in case of error
            try:
                correction_close = WebDriverWait(self.driver, 10) \
                    .until(EC.element_to_be_clickable((By.ID, cg.ALERT_EMPTY_RESULT)))
                # print("alert accepted")
                correction_close.click()
            except TimeoutException:
                print("no alert")
                pass
            try:
                pages = int([int(e) for e in 
                             self.driver.find_element(By.XPATH, cg.NUM_OF_RESULTS).get_attribute("innerText").split()
                             if e.isdigit()][0] / 10) + 1
            except NoSuchElementException as e3:
                pages = 2
            try:
                for p in range(1, pages + 1):
                    table = self.driver.find_element(By.XPATH, cg.RESULTS_TABLE)
                    # append element to lists
                    # license
                    self.license.extend(
                        [el.get_attribute("innerText") for el in table.find_elements(By.XPATH, cg.LICENSE)])
                    # name
                    self.name.extend([el.get_attribute("innerText") for el in table.find_elements(By.XPATH, cg.NAME)])
                    # mail
                    self.mail.extend([el.get_attribute("innerText") for el in table.find_elements(By.XPATH, cg.MAIL)])
                    # agency
                    self.agency.extend([el.get_attribute("innerText") for el in table.find_elements(By.XPATH, cg.AGENCY)])
                    # city
                    self.city.extend([city_selected] * len(table.find_elements(By.XPATH, cg.CITY)))
                    # is pensioni
                    self.is_pensioni.extend(
                        [el.get_attribute("innerText") for el in table.find_elements(By.XPATH, cg.IS_PENSIONI)])
                    # is elementar
                    self.is_elementar.extend(
                        [el.get_attribute("innerText") for el in table.find_elements(By.XPATH, cg.IS_ELEMENTAR)])
                    self.driver.find_element(By.XPATH, cg.NEXT_RESULTS_PAGE).click()  # click next
                    self.driver.implicitly_wait(10)
            except NoSuchElementException as e3:
                self.skipped.append(city_selected)
                continue
        return {'license': self.license,
                'name': self.name,
                'city': self.city,
                'is_pensioni': self.is_pensioni,
                'is_elementar': self.is_elementar}, self.skipped


if __name__ == '__main__':
    cities = pd.read_csv('cities2.csv', encoding='windows-1255')
    cities_list = cities['שם_ישוב'].sample(10).str.strip().tolist()
    scrapper1 = Scarper(name='one', cities_l=cities_list)
    driver1 = scrapper1.set_driver()
    data, skipped_items = scrapper1.extract()
    pd.DataFrame(data).to_csv('final'+scrapper1.get_name()+'.csv', index=False)
    print("skipped on: " + ','.join(skipped_items))
