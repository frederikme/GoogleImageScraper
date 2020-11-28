from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import urllib.request
from PIL import Image
import hashlib

import os
import time

class GoogleImageScraper:

    def __init__(self):
        # clear the console and show some basic info
        os.system("clear")
        text = '''   
 ____                                 
/ ___|  ___ _ __ __ _ _ __   ___ _ __ 
\___ \ / __| '__/ _` | '_ \ / _ \ '__|
 ___) | (__| | | (_| | |_) |  __/ |   
|____/ \___|_|  \__,_| .__/ \___|_|   
                     |_|              
        
        '''
        print(text)
        print("-> Made by Frederikme")
        print("-----------------------------------\n\n")

        self.links = []
        self.amount_to_scrape = 0
        self.amount_scraped = 0
        self.directory = "images"

        # getting chromedriver from cache or download from internet
        print("Getting ChromeDriver ...")
        self.browser = webdriver.Chrome(ChromeDriverManager().install())
        self.browser.get("https://www.google.com")
        time.sleep(2)
        self.acceptPolicies()

    def downloadImages(self, query, directory='images', amount=50):
        self.amount_to_scrape = amount - 1
        self.directory = directory

        self.searchFor(query)
        self.openImagesTab()
        self.links = self.getImageURLS()

        for link in self.links:
            self.storeImageAs(link)

    # Returns hash value of the image saved by the url given
    def storeImageAs(self, url, amount_of_attempts=1):
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

        # make 'undetectable' header to avoid being seen as scraper
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
            'Accept-Encoding': 'none',
            'Accept-Language': 'en-US,en;q=0.8',
            'Connection': 'keep-alive'}

        try:
            request_ = urllib.request.Request(url, None, headers)  # The assembled request
            response = urllib.request.urlopen(request_)  # store the response

        except Exception as e:
            if amount_of_attempts < 20:
                sleepy_time = amount_of_attempts * 30
                print("Attempt number {}: sleeping for {} seconds ...".format(amount_of_attempts, sleepy_time))
                time.sleep(sleepy_time)
                return self.storeImageAs(url, amount_of_attempts + 1)
            else:
                # Settle with the fact this one won't be stored
                error = "Amount of attempts exceeded in storage_helper\n" \
                        "attempting to get url: {}\n" \
                        "resulted in error: {}".format(url, e)
                print(error)
                return None

        temp_name = "temporary"

        if ".png" in url:
            # save as temporary file
            f = open("{}.png".format(temp_name), 'wb')
            f.write(response.read())
            f.close()

            # change png to jpg
            im = Image.open("{}/{}/{}.png".format(os.getcwd(), self.directory, temp_name))
            rgb_im = im.convert('RGB')
            rgb_im.save("{}/{}/{}.jpg".format(os.getcwd(), self.directory, temp_name))

            # remove the temporary file
            os.remove("{}.png".format(temp_name))

        elif '.webp' in url:
            # save as a temporary file
            f = open("{}.webp".format(temp_name), 'wb')
            f.write(response.read())
            f.close()

            # open the file and convert the file to jpeg
            im = Image.open("{}.webp".format(temp_name)).convert("RGB")
            # save the jpeg file in the directory it belongs
            im.save("{}/{}/{}.jpg".format(os.getcwd(), self.directory, temp_name), "jpeg")

            # remove the temporary file
            os.remove("{}.webp".format(temp_name))

        elif '.gif' in url:
            print("GIFS CANNOT BE STORED")
            return None

        # We assume its a jpg image
        else:
            f = open("{}/{}/{}.jpg".format(os.getcwd(), self.directory, temp_name), 'wb')
            f.write(response.read())
            f.close()

        # rename saved image to their hashvalue, so it's easy to compare (hashes of) images later on
        im = Image.open('{}/{}/{}.jpg'.format(os.getcwd(), self.directory, temp_name))
        hashvalue = hashlib.md5(im.tobytes()).hexdigest()

        os.rename('{}/{}/{}.jpg'.format(os.getcwd(), self.directory, temp_name),
                  '{}/{}/{}.jpg'.format(os.getcwd(), self.directory, hashvalue))

        print("Image saved as {}/{}/{}.jpg".format(os.getcwd(), self.directory, hashvalue))

        return hashvalue

    def getImageURLS(self):
        links = []

        try:
            class_name = 'rg_i'

            elements = self.browser.find_elements_by_class_name(class_name)

            max_scrolls = 20
            amount_scrolled = 0
            while self.amount_to_scrape + 5 > len(elements):
                self.scrollDownToLoadMore()
                time.sleep(2)
                elements = self.browser.find_elements_by_class_name(class_name)
                amount_scrolled += 1
                if amount_scrolled > max_scrolls:
                    break

            for el in elements:
                el.click()
                url = self.getImageURLOfOpenedImage()
                if url is not None:
                    links.append(url)
                    self.amount_scraped += 1
                    if self.amount_scraped > self.amount_to_scrape:
                        print(self.amount_scraped, self.amount_to_scrape)
                        print("Image urls scraped Succesfully")
                        return links

        except Exception as e:
            print(e)

    def getImageURLOfOpenedImage(self):
        try:
            class_name = 'qdnLaf'

            elements = self.browser.find_elements_by_class_name(class_name)

            for element in elements:
                el = element.find_elements_by_xpath('.//img[@src]')

                for e in el:
                    try:
                        src = e.get_attribute('src')
                        if src is not None:
                            if 'http' in src and src not in self.links:
                                return src
                    except:
                        print("ERROR HERE ..")
        except Exception as e:
            print(e)

        return None

    def scrollDownToLoadMore(self):
        self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

    def searchFor(self, query):
        try:
            xpath = '//input[@name="q"]'
            WebDriverWait(self.browser, 5).until(
                EC.presence_of_element_located((By.XPATH, xpath)))
            element = self.browser.find_element_by_xpath(xpath)
            element.send_keys(query)
            element.send_keys(Keys.ENTER)

        except Exception as e:
            print("Exception {}".format(e))

    def openImagesTab(self):
        try:
            xpath = '//*[@class="hide-focus-ring"]'
            WebDriverWait(self.browser, 5).until(
                EC.presence_of_element_located((By.XPATH, xpath)))
            elem = self.browser.find_elements_by_xpath(xpath)[0]
            elem.click()
        except Exception as e:
            print(e)

    def acceptPolicies(self):
        self.browser.switch_to.frame(self.browser.find_element_by_xpath('//*[@id="cnsw"]/iframe'))
        xpath = '//*[@id="introAgreeButton"]'

        try:
            acceptBtn = self.browser.find_element_by_xpath(xpath)
            acceptBtn.click()

            self.browser.switch_to.default_content()
        except Exception as e:
            # Pop up accept policies probably not presented
            print(e)

