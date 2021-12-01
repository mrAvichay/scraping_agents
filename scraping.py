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
from selenium.common.exceptions import NoSuchElementException,\
    ElementNotInteractableException,StaleElementReferenceException,\
    TimeoutException



def extract(cities_list):
    try:
        for i in range(0, len(cities_list)):
            city_selected = cities_list[i]
            print(city_selected)
            driver.implicitly_wait(10)

            search1=WebDriverWait(driver, 10,ignored_exceptions=ignored_exceptions).\
                until(EC.presence_of_element_located((By.ID, "e_1602060984227-254-72")))
            #search1 = driver.find_element(By.ID, "e_1602060984227-254-72")
            search1.send_keys(city_selected)
            search1.send_keys(Keys.RETURN)

            #try to locate the city at search engine menu
            try:
                driver.find_element(By.LINK_TEXT, "בחר").click()
                driver.find_element(By.ID, "e_1596528447512-995-1").click() #perform search
            except NoSuchElementException as e:
                driver.find_element(By.CLASS_NAME, "close-button-div").click() #close window in case of error

            driver.implicitly_wait(10)

            try:
                correction_close= WebDriverWait(driver, 100)\
                    .until(EC.element_to_be_clickable((By.ID,"close_correction_error")))
                #print("alert accepted")
                correction_close.click()
            except TimeoutException:
                #print("no alert")
                try:
                    pages = int([int(e) for e in
                                 driver.find_element(By.XPATH,
                                                     "//div[@class='TablePagerTotal']").get_attribute("innerText").split()
                                 if e.isdigit()][0] / 10) + 1
                except NoSuchElementException as e3:
                    pages = 2
                for p in range(1, pages+1):
                    table = driver.find_element(By.XPATH, "//table/tbody")
                    # append element to lists
                    # license
                    license.extend([el.get_attribute("innerText") for el in table.find_elements(By.XPATH, "//tr/td[1]")])
                    # name
                    name.extend([el.get_attribute("innerText") for el in table.find_elements(By.XPATH, "//tr/td[2]")])
                    # mail
                    mail.extend([el.get_attribute("innerText") for el in table.find_elements(By.XPATH, "//tr/td[3]")])
                    # agency
                    agency.extend([el.get_attribute("innerText") for el in table.find_elements(By.XPATH, "//tr/td[7]")])
                    # city
                    city.extend([city_selected] * len(table.find_elements(By.XPATH, "//tr/td[7]")))
                    # is pensioni
                    is_pensioni.extend([el.get_attribute("innerText") for el in table.find_elements(By.XPATH, "//tr/td[8]")])
                    # is elementar
                    is_elementar.extend([el.get_attribute("innerText") for el in table.find_elements(By.XPATH, "//tr/td[9]")])
                    driver.find_element(By.XPATH, "//a[@ng-switch-when='next']").click()  # click next
                    driver.implicitly_wait(10)
                    #driver.find_element(By.ID, "e_1596531064281-794-17").click()
            finally:
                #driver.find_element(By.ID, "e_1596531064281-794-17").click()  # clear screen
                #print("cllicked")
                driver.find_element(By.ID, "e_1602060984227-254-72").clear() #clear search text
                driver.implicitly_wait(20)
                print(len(license))
    except TimeoutException:
        print('random error')
    finally:
        return {'license': license,
                'name': name,
                'city': city,
                'is_pensioni': is_pensioni,
                'is_elementar': is_elementar}

if __name__=='__main__':
    cities = pd.read_csv('cities2.csv', encoding='windows-1255')
    cities_list = cities['שם_ישוב'].str.strip().tolist()

    driver = webdriver.Chrome(ChromeDriverManager().install())

    # access site
    driver.get("https://insa-prod-ex.formtitan.com/AgentsSearch#/")
    driver.implicitly_wait(10)

    driver.maximize_window()

    driver.implicitly_wait(10)

    # init lists
    license, \
    name, \
    mail, \
    agency, \
    city, \
    is_pensioni, \
    is_elementar = ([] for i in range(7))

    ignored_exceptions = (NoSuchElementException, StaleElementReferenceException,)

    select_choice = WebDriverWait(driver, 10, ignored_exceptions=ignored_exceptions) \
        .until(EC.presence_of_element_located((By.CLASS_NAME, 'select2-choice')))
    select_choice.click()
    agent_choice = WebDriverWait(driver, 10, ignored_exceptions=ignored_exceptions) \
        .until(EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='סוכן ביטוח']")))
    agent_choice.click()
    data=extract(cities_list)
    pd.DataFrame(data).to_csv('final.csv',index=False)

