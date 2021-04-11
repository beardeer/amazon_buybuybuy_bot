from selenium import webdriver
from time import sleep

# download Chrome driver at https://sites.google.com/a/chromium.org/chromedriver/
CHROME_DRIVER_PATH = 'replace with your local chrome driver path'

# amazon sigh in page
AMA_SIGIN_URL= 'https://www.amazon.com/ap/signin?openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.com%2F%3Fref_%3Dnav_custrec_signin&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=usflex&openid.mode=checkid_setup&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&'

# the stuff you want to buy
PRO_URL='https://www.amazon.com/gp/product/B000QSNYGI/ref=ppx_yo_dt_b_asin_title_o04_s00?ie=UTF8&psc=1'

MAX_PRICE = 10

# your amazon login info, DO NOT SHARE IT
EMAIL = 'xxx@gmail.com'
PASSSWORD = 'xxx'

# if test is true, the bot will not place order
IS_TEST = True


class BuyBuyBuyBot():
    def __init__(self):
        #  I am not sure why we need these, but it works, ref: https://stackoverflow.com/questions/56637973/how-to-fix-selenium-devtoolsactiveport-file-doesnt-exist-exception-in-python
        chromeOptions = webdriver.ChromeOptions() 
        chromeOptions.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2}) 
        chromeOptions.add_argument("--no-sandbox") 
        chromeOptions.add_argument("--disable-setuid-sandbox") 

        chromeOptions.add_argument("--remote-debugging-port=9222")

        chromeOptions.add_argument("--disable-dev-shm-using") 
        chromeOptions.add_argument("--disable-extensions") 
        chromeOptions.add_argument("--disable-gpu")
        chromeOptions.add_argument("disable-infobars")

        self.driver = webdriver.Chrome(options=chromeOptions, executable_path=CHROME_DRIVER_PATH)

    def login(self):
        # sign in to amazon.com
        self.driver.get(AMA_SIGIN_URL)
        input_box = self.driver.find_element_by_name('email')
        input_box.send_keys(EMAIL)
        input_box.submit()
        sleep(1)
        input_box = self.driver.find_element_by_name('password')
        input_box.send_keys(PASSSWORD)
        input_box.submit()

    def format_price(self, price_text):
        price = price_text.text
        price = price.replace('$', '')
        price = price.replace(',', '')
        price = price.replace('\n', '.')
        price = float(price)
        return price

    def check_price(self, max_price=0):
        try:
            print("Checking price, first try ... ")
            price_text = self.driver.find_element_by_xpath('//*[@id="price_inside_buybox"]')
            price = self.format_price(price_text)
            if price < max_price:
                return True, 1
            else:
                return False, 0
        except Exception as e:
            print(e)
            pass

        sleep(2)
        try:
            print("Checking price, second try ... ")
            see_all = self.driver.find_element_by_xpath('//*[@id="buybox-see-all-buying-choices"]')
            see_all.click()
            sleep(2)
            price = self.driver.find_element_by_xpath('//*[@id="aod-price-1"]')
            price = self.format_price(price)
            if price < max_price:
                return True, 2
            else:
                return False, 0
        except Exception as e:
            print(e)
            raise e
        return False, 0


    def no_coverage(self):
        # do not add amazon coverage
        try:
            no = self.driver.find_element_by_xpath('//*[@id="attachSiNoCoverage"]')
            no.click()
        except Exception as e:
            pass


    def check_and_buy(self):
        if IS_TEST == False:
            print(f"In prod model, trying to buy this item with ${MAX_PRICE}!!")
        sleep(3)  
        self.driver.get(PRO_URL)
        sleep(3)
        try:
            price_check, price_route = self.check_price(MAX_PRICE)
            assert (price_check), "Price is too high!!"
            print("Price is ok!")
            #  add to cart
            if price_route == 1:
                print("Price route 1")
                cart = self.driver.find_element_by_xpath('//*[@id="add-to-cart-button"]')
                cart.click()
            elif price_route == 2:
                print("Price route 2")
                cart = self.driver.find_element_by_name('submit.addToCart')
                cart.click()
            sleep(2)
            self.no_coverage()
            sleep(2)
            # check out
            checkout = self.driver.find_element_by_xpath('//*[@id="hlb-ptc-btn"]')
            checkout.click()
            sleep(2)
            # place order
            if IS_TEST == False:
                buy = self.driver.find_element_by_name('placeYourOrder1')  
                buy.click()
                print('Order placed!')
            else:
                print('In test model, order not placed!')
            sleep(3)
            self.driver.close()
        except Exception as e:
            print(e)
            sleep(3)
            self.check_and_buy()


bot = BuyBuyBuyBot()
bot.login()
bot.check_and_buy()