import pandas as pd
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, \
    StaleElementReferenceException,\
    TimeoutException, ElementClickInterceptedException
import config as cg
from udf import init_logger


class Scarper:
    def __init__(self, scrapper_name, cities_l, logger=None):
        self.scrapper_name = scrapper_name
        self.cities = cities_l
        self.logger = logger
        self.license, \
        self.name, \
        self.mail, \
        self.agency, \
        self.city, \
        self.is_pensioni, \
        self.is_elementar = ([] for i in range(7))
        self.ignored_exceptions = (NoSuchElementException,
                                   StaleElementReferenceException,
                                   ElementClickInterceptedException)
        self.site = cg.SITE
        self.driver = webdriver.Chrome(ChromeDriverManager().install())
        self.skipped = []

    def set_driver(self):
        # access site
        if self.logger:
            self.logger.info('accessing site')
        self.driver.get(self.site)
        self.driver.implicitly_wait(10)
        self.driver.maximize_window()

    def get_name(self):
        return str(self.scrapper_name)

    def extract(self):
        if self.logger:
            self.logger.info('starting scraper:'+self.get_name())

        #drop down list
        try:
            select_choice1 = WebDriverWait(self.driver, 10, ignored_exceptions=self.ignored_exceptions) \
                .until(EC.presence_of_element_located((By.CLASS_NAME, cg.DROP_DOWN_LICENSE)))
            select_choice1.click()
        except TimeoutException as t1:
            if self.logger:
                self.logger.error('Error - Drop-Down List was not found')

        #select agent on drop down menu
        try:
            agent_choice1 = WebDriverWait(self.driver, 10, ignored_exceptions=self.ignored_exceptions) \
                .until(EC.element_to_be_clickable((By.XPATH, cg.AGENT_DD_CHOICE)))
            agent_choice1.click()
        except TimeoutException as t1:
            if self.logger:
                self.logger.error('Error - Agent Option at drop-down list was not found')

        #looping over cities
        for i in range(0, len(self.cities)):
            city_selected = self.cities[i]
            if self.logger:
                self.logger.info('current city: '+city_selected)

            #entering text into search box
            try:
                search1 = WebDriverWait(self.driver, 10, ignored_exceptions=self.ignored_exceptions). \
                    until(EC.presence_of_element_located((By.ID, cg.SEARCH_BOX)))
                search1.clear()
                search1.send_keys(city_selected)
                search1.send_keys(Keys.RETURN)
            except TimeoutException:
                if self.logger:
                    self.logger.error('search for '+city_selected+'failed, skipping...')
                self.skipped.append(city_selected)
                continue

            #attempt clicking on link at search box
            try:
                select_link = WebDriverWait(self.driver, 10, ignored_exceptions=self.ignored_exceptions) \
                    .until(EC.element_to_be_clickable((By.LINK_TEXT, cg.LINK_SELECT)))
                select_link.click()
            except (TimeoutException, ElementClickInterceptedException) as e:
                if self.logger:
                    self.logger.info('no results for ' + city_selected + ',skipping...')
                try:
                    if self.logger:
                        self.logger.info('exiting search')
                    # close window in case of error
                    close_button = WebDriverWait(self.driver, 10, ignored_exceptions=self.ignored_exceptions) \
                        .until(EC.element_to_be_clickable((By.CLASS_NAME, cg.SELECT_CLOSE_BUTTON)))
                    close_button.click()
                except TimeoutException as e:
                    if self.logger:
                        self.logger.error('failed to close search window as it does not appear')
                    continue
                continue

            # click on search
            try:
                search_button = WebDriverWait(self.driver, 10, ignored_exceptions=self.ignored_exceptions) \
                    .until(EC.element_to_be_clickable((By.ID, cg.SEARCH_BUTTON)))
                search_button.click()
            except TimeoutException as e:
                if self.logger:
                    self.logger.error(
                        'failed clicking on search while looking for' + city_selected + ',skipping...')
                continue

            #check for empty results window
            try:
                correction_close = WebDriverWait(self.driver, 10) \
                    .until(EC.element_to_be_clickable((By.ID, cg.ALERT_EMPTY_RESULT)))
                correction_close.click()
                continue

            #ok as there are results
            except TimeoutException:
                if self.logger:
                    self.logger.info('no alert for '+city_selected)
                pass

            #trying to extract how many pages are displayed
            try:
                pages = int([int(e) for e in 
                             self.driver.find_element(By.XPATH, cg.NUM_OF_RESULTS).get_attribute("innerText").split()
                             if e.isdigit()][0] / 10) + 1
            except NoSuchElementException as e3:
                pages = 2

            #extract results for each page
            try:
                if self.logger:
                    self.logger.info('extracting results for '+city_selected)
                for p in range(1, pages + 1):

                    #trying to extract table
                    try:
                        table = WebDriverWait(self.driver, 10, ignored_exceptions=self.ignored_exceptions) \
                            .until(EC.presence_of_element_located((By.XPATH, cg.RESULTS_TABLE)))
                    except TimeoutException as e:
                        if self.logger:
                            self.logger.error('failed to show results for '+city_selected+',skipping...')
                        raise StopIteration

                    # append element to lists
                    # license
                    try:
                        self.license.extend(
                            [el.get_attribute("innerText") for el in table.find_elements(By.XPATH, cg.LICENSE)])

                    # name
                        self.name.extend([el.get_attribute("innerText") for el in table.find_elements(By.XPATH,cg.NAME)])

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

                        if self.logger:
                            self.logger.info('appending results for '+city_selected)

                    except (NoSuchElementException,StaleElementReferenceException) as e:
                        if self.logger:
                            logging.error('error while trying to extract results')
                        continue

                    try:
                        if self.logger:
                            self.logger.info('trying next page for '+city_selected)
                        next_page = WebDriverWait(self.driver, 10, ignored_exceptions=self.ignored_exceptions) \
                            .until(EC.element_to_be_clickable((By.XPATH, cg.NEXT_RESULTS_PAGE)))
                        next_page.click()  # click next
                    except TimeoutException as e:
                        if self.logger:
                            self.logger.info('no next page for '+city_selected+', continue to next city')
                        continue

            except StopIteration:
                if self.logger:
                    self.logger.info('skipping '+city_selected+' because no results were found...')
                self.skipped.append(city_selected)
                continue

        if self.logger:
            self.logger.info('closing scraper '+self.get_name())
        self.driver.close()

        return {'license': self.license,
                'name': self.name,
                'city': self.city,
                'is_pensioni': self.is_pensioni,
                'is_elementar': self.is_elementar}, self.skipped


if __name__ == '__main__':
    logger, handler = init_logger()
    logger.info('starting logger')
    logger.info('reading cities list')
    cities = pd.read_csv('cities2.csv', encoding='windows-1255')
    cities_list = ['סוסיה', 'תל אביב','חיפה', 'קרית שמונה']#cities['שם_ישוב'].sample(10).str.strip().tolist()
    print(','.join(cities_list))
    scrapper1 = Scarper(scrapper_name='one', cities_l=cities_list, logger=logger)
    scrapper1.set_driver()
    data, skipped_items = scrapper1.extract()
    pd.DataFrame(data).to_csv('final_'+scrapper1.get_name()+'.csv', index=False)
    print("skipped on: " + ','.join(skipped_items))
    logger.info('finished successfully')
    logger.removeHandler(handler)
